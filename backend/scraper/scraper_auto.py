#!/usr/bin/env python3
"""
Scraper Automático de DropKiller - Estrategas IA v4.4
Debug mode para ver estructura de filas
"""

import os
import sys
import json
import re
import argparse
import asyncio
import requests
from datetime import datetime
from typing import List, Dict

from dotenv import load_dotenv

load_dotenv()

# ============== CONFIG ==============
DROPKILLER_EMAIL = os.getenv("DROPKILLER_EMAIL", "")
DROPKILLER_PASSWORD = os.getenv("DROPKILLER_PASSWORD", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

DROPKILLER_COUNTRIES = {
    "CO": "65c75a5f-0c4a-45fb-8c90-5b538805a15a",
    "MX": "98993bd0-955a-4fa3-9612-c9d4389c44d0", 
    "EC": "82811e8b-d17d-4ab9-847a-fa925785d566",
}


# ============== SUPABASE ==============
class SupabaseClient:
    def __init__(self, url: str, key: str):
        self.url = url.rstrip('/')
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
    
    def upsert(self, table: str, data: dict) -> bool:
        url = f"{self.url}/rest/v1/{table}"
        headers = {**self.headers, "Prefer": "resolution=merge-duplicates"}
        response = requests.post(url, headers=headers, json=data)
        return response.status_code in [200, 201, 204]


# ============== DROPKILLER SCRAPER ==============
class DropKillerScraper:
    def __init__(self, email: str, password: str, debug: bool = False):
        self.email = email
        self.password = password
        self.browser = None
        self.page = None
        self.debug = debug
    
    async def init_browser(self, headless: bool = True):
        from playwright.async_api import async_playwright
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(60000)
    
    async def login(self) -> bool:
        print("  [1] Iniciando login...")
        
        try:
            await self.page.goto('https://app.dropkiller.com/sign-in', wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(5)
            
            email_input = None
            for selector in ['input#identifier-field', 'input[name="identifier"]', 'input[type="email"]']:
                try:
                    email_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if email_input:
                        break
                except:
                    continue
            
            if not email_input:
                return False
            
            await email_input.fill(self.email)
            await asyncio.sleep(1)
            
            password_input = None
            for selector in ['input#password-field', 'input[type="password"]']:
                try:
                    password_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if password_input:
                        break
                except:
                    continue
            
            if not password_input:
                return False
            
            await password_input.fill(self.password)
            await asyncio.sleep(1)
            
            try:
                submit_btn = await self.page.wait_for_selector('button:has-text("Iniciar")', timeout=3000)
                await submit_btn.click()
            except:
                await password_input.press('Enter')
            
            try:
                await self.page.wait_for_url('**/dashboard**', timeout=30000)
                print("  [✓] Login exitoso")
                return True
            except:
                if '/dashboard' in self.page.url:
                    print("  [✓] Login exitoso")
                    return True
                return False
            
        except Exception as e:
            print(f"  [✗] Error: {e}")
            return False
    
    async def extract_products_from_page(self) -> List[Dict]:
        """Extrae productos - DEBUG VERSION para ver estructura"""
        debug_mode = self.debug
        
        return await self.page.evaluate(f'''() => {{
            const products = [];
            const seen = new Set();
            const debugMode = {str(debug_mode).lower()};
            
            // Buscar todas las filas de la tabla que contienen productos
            // En DropKiller, cada fila tiene: imagen, nombre+proveedor+stock, banderas, ID, precio, ganancia, ventas, botón
            const rows = document.querySelectorAll('tr, [role="row"]');
            
            if (debugMode) {{
                console.log('Total rows found:', rows.length);
            }}
            
            // También buscar por Ver detalle
            const buttons = document.querySelectorAll('button');
            const detailButtons = Array.from(buttons).filter(el => 
                el.innerText && el.innerText.trim() === 'Ver detalle'
            );
            
            if (debugMode) {{
                console.log('Ver detalle buttons found:', detailButtons.length);
            }}
            
            for (const btn of detailButtons) {{
                // Encontrar el contenedor de la fila
                let row = btn.closest('tr') || btn.parentElement;
                
                // Si no es tr, subir hasta encontrar un contenedor con todos los datos
                if (!row || row.tagName !== 'TR') {{
                    row = btn.parentElement;
                    for (let i = 0; i < 10 && row; i++) {{
                        const text = row.innerText || '';
                        if (text.includes('Stock:') && text.includes('COP') && text.includes('Ver detalle')) {{
                            break;
                        }}
                        row = row.parentElement;
                    }}
                }}
                
                if (!row) continue;
                
                const text = row.innerText || '';
                
                if (debugMode && products.length < 3) {{
                    console.log('=== ROW TEXT ===');
                    console.log(text);
                    console.log('================');
                }}
                
                // Buscar todos los números en el texto
                // Estructura esperada: nombre, proveedor, Stock: XXX, ID, XX.XXX COP, XX.XXX COP, VENTAS, Ver detalle
                
                // Extraer Stock
                const stockMatch = text.match(/Stock:\\s*([\\d.,]+)/i);
                const stock = stockMatch ? parseInt(stockMatch[1].replace(/[.,]/g, '')) : 0;
                
                // Extraer precios (XX.XXX COP)
                const pricePattern = /([\\d.]+)\\s*COP/g;
                const prices = [];
                let match;
                while ((match = pricePattern.exec(text)) !== null) {{
                    const price = parseInt(match[1].replace(/\\./g, ''));
                    if (price >= 1000 && price <= 500000) {{
                        prices.push(price);
                    }}
                }}
                
                let providerPrice = prices.length > 0 ? prices[0] : 0;
                let profit = prices.length > 1 ? prices[1] : 0;
                
                // VENTAS: El número después del último COP pero antes de "Ver detalle"
                const lastCOPMatch = text.match(/COP[^C]*$/);
                let sales7d = 0;
                
                if (lastCOPMatch) {{
                    // Buscar el texto entre el último COP y "Ver detalle"
                    const afterLastCOP = text.substring(text.lastIndexOf('COP') + 3);
                    const beforeVerDetalle = afterLastCOP.split('Ver detalle')[0];
                    
                    if (debugMode && products.length < 3) {{
                        console.log('After last COP:', beforeVerDetalle);
                    }}
                    
                    // Buscar números en este segmento
                    // El formato puede ser "49" o "1.502" (con punto como separador de miles)
                    const salesMatch = beforeVerDetalle.match(/([\\d.]+)/);
                    if (salesMatch) {{
                        // Remover puntos (separador de miles) y convertir
                        sales7d = parseInt(salesMatch[1].replace(/\\./g, '')) || 0;
                    }}
                }}
                
                if (debugMode && products.length < 3) {{
                    console.log('Extracted sales7d:', sales7d);
                }}
                
                // Buscar nombre del producto
                const lines = text.split('\\n').map(l => l.trim()).filter(l => l);
                let name = '';
                
                for (const line of lines) {{
                    if (/^\\d{{1,2}}[\\/-]\\d{{1,2}}[\\/-]\\d{{2,4}}$/.test(line)) continue;
                    if (/^[\\d.,\\s]+$/.test(line)) continue;
                    if (/COP/.test(line)) continue;
                    if (line.startsWith('Stock:') || line.startsWith('Proveedor:')) continue;
                    if (line.includes('Ver detalle') || line === 'ID') continue;
                    if (/^(Ventas|Facturación|Fecha|Página|Mostrar)/i.test(line)) continue;
                    if (line.length < 8 || line.length > 80) continue;
                    
                    const lower = line.toLowerCase();
                    const providerWords = ['shop', 'store', 'tienda', 'import', 'mayor', 
                                           'group', 'china', 'bodeguita', 'inversiones',
                                           'fragance', 'glow', 'perfumeria', 'goldbox',
                                           'vitalcom', 'worldsport', 'homie', 'tulastore',
                                           'diversidades', 'agrostock', 'krombi', 'fajas',
                                           'stockeado', 'prendas control', 'dads jackets',
                                           'toons mayorista', 'oh homie'];
                    if (providerWords.some(w => lower.includes(w))) continue;
                    
                    const words = line.split(/\\s+/);
                    if (words.length === 1 && line.length < 12) continue;
                    
                    name = line;
                    break;
                }}
                
                if (!name || providerPrice === 0) continue;
                
                const uniqueKey = name.substring(0, 25) + '_' + providerPrice;
                if (seen.has(uniqueKey)) continue;
                seen.add(uniqueKey);
                
                products.push({{
                    name: name.substring(0, 60),
                    providerPrice,
                    profit,
                    stock,
                    sales7d,
                    sales30d: 0,
                    externalId: uniqueKey.replace(/[^a-zA-Z0-9_]/g, '')
                }});
            }}
            
            return products;
        }}''')
    
    async def get_products(self, country: str = "CO", min_sales: int = 20, max_products: int = 100, max_pages: int = 5) -> List[Dict]:
        """Extrae productos de DropKiller con paginación por URL"""
        print(f"  [2] Navegando a productos (ventas >= {min_sales})...")
        
        country_id = DROPKILLER_COUNTRIES.get(country, DROPKILLER_COUNTRIES["CO"])
        
        all_products = []
        seen_ids = set()
        consecutive_empty = 0
        
        try:
            for page_num in range(1, max_pages + 1):
                url = f"https://app.dropkiller.com/dashboard/products?country={country_id}&limit=50&page={page_num}&s7min={min_sales}"
                
                print(f"      Página {page_num}/{max_pages}...", end=" ", flush=True)
                await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await asyncio.sleep(4)
                
                for _ in range(3):
                    await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    await asyncio.sleep(0.5)
                await self.page.evaluate('window.scrollTo(0, 0)')
                await asyncio.sleep(1)
                
                page_products = await self.extract_products_from_page()
                
                new_count = 0
                for p in page_products:
                    pid = p.get('externalId', '')
                    if pid not in seen_ids:
                        seen_ids.add(pid)
                        all_products.append(p)
                        new_count += 1
                
                print(f"→ {len(page_products)} extraídos, {new_count} nuevos | Total: {len(all_products)}")
                
                if new_count == 0:
                    consecutive_empty += 1
                    if consecutive_empty >= 2:
                        print(f"      ✓ Sin productos nuevos, terminando...")
                        break
                else:
                    consecutive_empty = 0
                
                if len(all_products) >= max_products:
                    print(f"      ✓ Alcanzado límite de {max_products} productos")
                    break
                
                if len(page_products) == 0:
                    print(f"      ✓ Página vacía, terminando...")
                    break
            
            await self.page.screenshot(path='debug_products.png')
            
            all_products = [p for p in all_products if p.get('sales7d', 0) >= min_sales][:max_products]
            
            print(f"  [✓] Total: {len(all_products)} productos con ventas >= {min_sales}")
            
            if all_products:
                print(f"      Ejemplos:")
                for p in all_products[:5]:
                    print(f"        - {p['name'][:40]} | ${p['providerPrice']:,} | V7d:{p['sales7d']}")
            
            return all_products
            
        except Exception as e:
            print(f"  [✗] Error: {e}")
            import traceback
            traceback.print_exc()
            return all_products


    async def close(self):
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            await self.playwright.stop()


# ============== ANALYZER ==============
def calculate_margin(cost_price: int) -> Dict:
    if cost_price <= 0:
        cost_price = 35000
    
    shipping = 18000
    cpa = 25000
    effective_rate = 0.63
    
    fixed_costs = shipping + cpa + (shipping * 0.22 * 0.5)
    total_cost = cost_price + fixed_costs
    breakeven_price = int(total_cost / effective_rate)
    optimal_price = ((int(breakeven_price * 1.30) // 1000) * 1000) + 900
    
    effective_revenue = optimal_price * effective_rate
    net_margin = effective_revenue - total_cost
    roi = (net_margin / total_cost) * 100 if total_cost > 0 else 0
    
    return {
        "cost_price": cost_price,
        "breakeven_price": breakeven_price,
        "optimal_price": optimal_price,
        "net_margin": int(net_margin),
        "roi": round(roi, 1),
        "multiplier": round(optimal_price / cost_price, 1) if cost_price > 0 else 0,
    }


def calculate_viability(product: Dict, margin: Dict) -> tuple:
    score = 0
    reasons = []
    
    recent_sales = product.get('sales7d', 0)
    stock = product.get('stock', 0)
    estimated_stock = max(stock, recent_sales * 2) if recent_sales > 0 else stock
    
    if recent_sales >= 100:
        score += 40
        reasons.append(f"🔥 Ventas excelentes: {recent_sales}/7d")
    elif recent_sales >= 50:
        score += 35
        reasons.append(f"Ventas muy altas: {recent_sales}/7d")
    elif recent_sales >= 30:
        score += 28
        reasons.append(f"Ventas altas: {recent_sales}/7d")
    elif recent_sales >= 15:
        score += 20
        reasons.append(f"Ventas buenas: {recent_sales}/7d")
    elif recent_sales >= 5:
        score += 12
        reasons.append(f"Ventas moderadas: {recent_sales}/7d")
    else:
        reasons.append(f"Sin ventas: {recent_sales}/7d")
    
    roi = margin.get("roi", 0)
    if roi >= 25:
        score += 25
        reasons.append(f"ROI excelente: {roi}%")
    elif roi >= 15:
        score += 18
        reasons.append(f"ROI bueno: {roi}%")
    elif roi > 0:
        score += 8
        reasons.append(f"ROI bajo: {roi}%")
    
    score += 12
    
    if estimated_stock >= 50:
        score += 15
        reasons.append(f"Stock: {estimated_stock}")
    elif estimated_stock > 0:
        score += 8
    
    verdict = "EXCELENTE" if score >= 70 else "VIABLE" if score >= 50 else "ARRIESGADO" if score >= 30 else "NO_RECOMENDADO"
    
    return score, reasons, verdict, recent_sales, estimated_stock


def analyze_with_claude(product: Dict, margin: Dict) -> Dict:
    if not ANTHROPIC_API_KEY:
        return {"recommendation": "REVISAR", "unused_angles": [], "optimal_price": margin["optimal_price"]}
    
    prompt = f"""Analiza este producto dropshipping Colombia:

Producto: {product.get('name', 'N/A')}
Costo: ${margin['cost_price']:,} COP
Precio óptimo: ${margin['optimal_price']:,} COP ({margin['multiplier']}x)
Margen: ${margin['net_margin']:,} COP
ROI: {margin['roi']}%
Ventas 7d: {product.get('sales7d', 0)}

JSON solo:
{{"recommendation": "VENDER" o "NO_VENDER", "confidence": 1-10, "optimal_price": numero, "unused_angles": ["angulo1", "angulo2"], "key_insight": "oracion"}}"""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 400, "messages": [{"role": "user", "content": prompt}]},
            timeout=30
        )
        if response.status_code == 200:
            text = response.json()["content"][0]["text"]
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            return json.loads(text)
    except:
        pass
    
    return {"recommendation": "REVISAR", "unused_angles": [], "optimal_price": margin["optimal_price"]}


# ============== MAIN ==============
async def main():
    parser = argparse.ArgumentParser(description="DropKiller Scraper v4.4")
    parser.add_argument("--min-sales", type=int, default=20, help="Ventas mínimas 7d")
    parser.add_argument("--max-products", type=int, default=100, help="Máx productos")
    parser.add_argument("--max-pages", type=int, default=5, help="Máx páginas")
    parser.add_argument("--country", default="CO", help="País")
    parser.add_argument("--no-ai", action="store_true", help="Sin Claude")
    parser.add_argument("--visible", action="store_true", help="Mostrar navegador")
    parser.add_argument("--debug", action="store_true", help="Modo debug - muestra estructura de filas")
    args = parser.parse_args()
    
    if not DROPKILLER_EMAIL or not DROPKILLER_PASSWORD:
        print("ERROR: Falta DROPKILLER_EMAIL o DROPKILLER_PASSWORD en .env")
        sys.exit(1)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Falta SUPABASE_URL o SUPABASE_KEY en .env")
        sys.exit(1)
    
    print("=" * 65)
    print(f"  ESTRATEGAS IA - Scraper v4.4 {'(DEBUG)' if args.debug else ''}")
    print("=" * 65)
    print(f"  País: {args.country} | Ventas mín: {args.min_sales}")
    print(f"  Máx productos: {args.max_products} | Máx páginas: {args.max_pages}")
    print("=" * 65)
    
    scraper = DropKillerScraper(DROPKILLER_EMAIL, DROPKILLER_PASSWORD, debug=args.debug)
    supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
    
    stats = {"scraped": 0, "analyzed": 0, "recommended": 0}
    
    try:
        print("\n[FASE 1] Login")
        await scraper.init_browser(headless=not args.visible)
        
        if not await scraper.login():
            print("\nERROR: Login fallido")
            return
        
        print("\n[FASE 2] Extracción")
        products = await scraper.get_products(args.country, args.min_sales, args.max_products, args.max_pages)
        
        if not products:
            print("\nNo se encontraron productos.")
            return
        
        stats["scraped"] = len(products)
        
        if args.debug:
            print("\n[DEBUG] Primeros 5 productos extraídos:")
            for p in products[:5]:
                print(f"  {p['name'][:40]} | Precio:{p['providerPrice']} | Stock:{p['stock']} | V7d:{p['sales7d']}")
        
        print(f"\n[FASE 3] Análisis de {len(products)} productos\n")
        
        recommended = []
        
        for i, product in enumerate(products, 1):
            ext_id = product.get("externalId", f"prod_{i}")
            name = product.get("name", "Sin nombre")[:40]
            cost = product.get("providerPrice", 35000)
            sales7d = product.get("sales7d", 0)
            sales30d = product.get("sales30d", 0)
            stock = product.get("stock", 0)
            
            print(f"  [{i}/{len(products)}] {name}")
            
            margin = calculate_margin(cost)
            score, reasons, verdict, _, _ = calculate_viability(product, margin)
            
            print(f"      V7d:{sales7d} | ${cost:,} | ROI:{margin['roi']}%")
            
            stats["analyzed"] += 1
            
            ai_result = {"recommendation": verdict, "unused_angles": [], "optimal_price": margin["optimal_price"]}
            if not args.no_ai and ANTHROPIC_API_KEY and score >= 30 and sales7d >= 5:
                ai_result = analyze_with_claude(product, margin)
            
            is_recommended = score >= 50 and margin["roi"] >= 15 and sales7d >= 10 and ai_result.get("recommendation") != "NO_VENDER"
            
            if is_recommended:
                stats["recommended"] += 1
                print(f"      ✅ RECOMENDADO (Score:{score})")
                recommended.append({
                    "name": name, "sales7d": sales7d, "sales30d": sales30d,
                    "margin": margin["net_margin"], "score": score, "cost": cost
                })
            
            data = {
                "external_id": ext_id,
                "platform": "dropi",
                "country_code": args.country,
                "name": name,
                "cost_price": cost,
                "suggested_price": margin["optimal_price"],
                "optimal_price": ai_result.get("optimal_price", margin["optimal_price"]),
                "sales_7d": sales7d,
                "sales_30d": sales30d,
                "current_stock": stock,
                "real_margin": margin["net_margin"],
                "roi": margin["roi"],
                "breakeven_price": margin["breakeven_price"],
                "viability_score": score,
                "viability_verdict": verdict,
                "score_reasons": reasons,
                "unused_angles": ai_result.get("unused_angles", []),
                "ai_recommendation": ai_result.get("recommendation", verdict),
                "ai_analysis": json.dumps(ai_result),
                "is_recommended": is_recommended,
                "analyzed_at": datetime.now().isoformat()
            }
            
            supabase.upsert("analyzed_products", data)
        
        print("\n" + "=" * 65)
        print("  RESUMEN")
        print("=" * 65)
        print(f"  Scrapeados: {stats['scraped']}")
        print(f"  Analizados: {stats['analyzed']}")
        print(f"  Recomendados: {stats['recommended']}")
        
        if recommended:
            print(f"\n  🏆 TOP 10:")
            for p in sorted(recommended, key=lambda x: x["sales7d"], reverse=True)[:10]:
                print(f"     • {p['name'][:30]} | V7d:{p['sales7d']} | ${p['cost']:,}")
        
        print("=" * 65)
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
