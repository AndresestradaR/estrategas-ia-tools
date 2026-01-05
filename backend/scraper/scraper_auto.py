#!/usr/bin/env python3
"""
Scraper Automático de DropKiller - Estrategas IA v4.6
Extracción correcta: ventas están entre ganancia COP y facturación COP
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
    
    async def extract_raw_rows(self, limit: int = 3) -> List[str]:
        """Extrae el texto raw de las primeras filas para debug"""
        return await self.page.evaluate(f'''() => {{
            const rows = [];
            const buttons = document.querySelectorAll('button');
            const detailButtons = Array.from(buttons).filter(el => 
                el.innerText && el.innerText.trim() === 'Ver detalle'
            );
            
            for (let i = 0; i < Math.min(detailButtons.length, {limit}); i++) {{
                const btn = detailButtons[i];
                let row = btn.parentElement;
                for (let j = 0; j < 10 && row; j++) {{
                    const text = row.innerText || '';
                    if (text.includes('Stock:') && text.includes('COP') && text.includes('Ver detalle')) {{
                        break;
                    }}
                    row = row.parentElement;
                }}
                if (row) {{
                    rows.push(row.innerText);
                }}
            }}
            return rows;
        }}''')
    
    async def extract_products_from_page(self) -> List[Dict]:
        """Extrae productos - estructura correcta de DropKiller"""
        return await self.page.evaluate('''() => {
            const products = [];
            const seen = new Set();
            
            const buttons = document.querySelectorAll('button');
            const detailButtons = Array.from(buttons).filter(el => 
                el.innerText && el.innerText.trim() === 'Ver detalle'
            );
            
            for (const btn of detailButtons) {
                let row = btn.parentElement;
                for (let i = 0; i < 10 && row; i++) {
                    const text = row.innerText || '';
                    if (text.includes('Stock:') && text.includes('COP') && text.includes('Ver detalle')) {
                        break;
                    }
                    row = row.parentElement;
                }
                
                if (!row) continue;
                
                const text = row.innerText || '';
                const lines = text.split('\\n').map(l => l.trim()).filter(l => l);
                
                // Extraer Stock
                const stockMatch = text.match(/Stock:\\s*([\\d.,]+)/i);
                const stock = stockMatch ? parseInt(stockMatch[1].replace(/[.,]/g, '')) : 0;
                
                // Estructura de DropKiller:
                // [nombre, Proveedor:, proveedor, Stock: X, ID, PRECIO COP, GANANCIA COP, V7D, V30D, FACT7D COP, FACT30D COP, fecha, categoria, Ver detalle]
                
                // Encontrar índices de líneas con COP
                const copIndices = [];
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i].includes('COP')) {
                        copIndices.push(i);
                    }
                }
                
                // Necesitamos al menos 4 COP (precio, ganancia, fact7d, fact30d)
                if (copIndices.length < 4) continue;
                
                // Precio proveedor = primer COP
                // Ganancia = segundo COP
                // Las ventas están ENTRE el segundo COP y el tercer COP
                const precioLine = lines[copIndices[0]];
                const gananciaLine = lines[copIndices[1]];
                
                // Extraer precio y ganancia
                const extractPrice = (line) => {
                    const match = line.match(/([\\d.]+)\\s*COP/);
                    if (match) {
                        return parseInt(match[1].replace(/\\./g, ''));
                    }
                    return 0;
                };
                
                const providerPrice = extractPrice(precioLine);
                const profit = extractPrice(gananciaLine);
                
                // Ventas 7d y 30d están justo después del segundo COP
                // Son las líneas entre copIndices[1] y copIndices[2]
                let sales7d = 0;
                let sales30d = 0;
                
                const salesStartIndex = copIndices[1] + 1;
                const salesEndIndex = copIndices[2];
                
                const salesLines = [];
                for (let i = salesStartIndex; i < salesEndIndex; i++) {
                    const line = lines[i];
                    // Solo números (pueden tener . como separador de miles)
                    const cleaned = line.replace(/\\./g, '');
                    if (/^\\d+$/.test(cleaned)) {
                        salesLines.push(parseInt(cleaned));
                    }
                }
                
                if (salesLines.length >= 1) sales7d = salesLines[0];
                if (salesLines.length >= 2) sales30d = salesLines[1];
                
                // Buscar nombre del producto (primera línea válida)
                let name = '';
                for (const line of lines) {
                    // Excluir líneas no válidas
                    if (/^\\d{1,2}[\\/-]\\d{1,2}[\\/-]\\d{2,4}$/.test(line)) continue;
                    if (/^[\\d.,\\s]+$/.test(line)) continue;
                    if (/COP/.test(line)) continue;
                    if (line.startsWith('Stock:') || line.startsWith('Proveedor:') || line === 'Proveedor:') continue;
                    if (line.includes('Ver detalle') || line === 'ID') continue;
                    if (/^(Ventas|Facturación|Fecha|Página|Mostrar)/i.test(line)) continue;
                    if (line.length < 5 || line.length > 80) continue;
                    
                    // Excluir nombres de proveedores conocidos
                    const lower = line.toLowerCase();
                    const providerWords = ['shop', 'store', 'tienda', 'import', 'mayor', 
                                           'group', 'china', 'bodeguita', 'inversiones',
                                           'fragance', 'glow', 'perfumeria', 'goldbox',
                                           'vitalcom', 'worldsport', 'homie', 'tulastore',
                                           'diversidades', 'agrostock', 'krombi', 'fajas',
                                           'stockeado', 'prendas control', 'dads jackets',
                                           'toons mayorista', 'oh homie'];
                    if (providerWords.some(w => lower.includes(w))) continue;
                    
                    // Excluir categorías comunes
                    const categories = ['herramientas', 'belleza', 'deportes', 'hogar', 'salud', 
                                       'tecnologia', 'moda', 'mascotas', 'bebes', 'cocina'];
                    if (categories.includes(lower)) continue;
                    
                    name = line;
                    break;
                }
                
                if (!name || providerPrice === 0) continue;
                
                const uniqueKey = name.substring(0, 25) + '_' + providerPrice;
                if (seen.has(uniqueKey)) continue;
                seen.add(uniqueKey);
                
                products.push({
                    name: name.substring(0, 60),
                    providerPrice,
                    profit,
                    stock,
                    sales7d,
                    sales30d,
                    externalId: uniqueKey.replace(/[^a-zA-Z0-9_]/g, '')
                });
            }
            
            return products;
        }''')
    
    async def get_products(self, country: str = "CO", min_sales: int = 20, max_products: int = 100, max_pages: int = 5) -> List[Dict]:
        """Extrae productos de DropKiller"""
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
                
                # Debug: mostrar texto raw de primeras filas
                if self.debug and page_num == 1:
                    raw_rows = await self.extract_raw_rows(3)
                    print("\n\n[DEBUG] Texto raw de primeras 3 filas:")
                    for i, row_text in enumerate(raw_rows):
                        print(f"\n--- FILA {i+1} ---")
                        print(row_text[:600])
                        print("--- FIN FILA ---")
                    print()
                
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
                    print(f"        - {p['name'][:40]} | ${p['providerPrice']:,} | V7d:{p['sales7d']} V30d:{p['sales30d']}")
            
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
    parser = argparse.ArgumentParser(description="DropKiller Scraper v4.6")
    parser.add_argument("--min-sales", type=int, default=20, help="Ventas mínimas 7d")
    parser.add_argument("--max-products", type=int, default=100, help="Máx productos")
    parser.add_argument("--max-pages", type=int, default=5, help="Máx páginas")
    parser.add_argument("--country", default="CO", help="País")
    parser.add_argument("--no-ai", action="store_true", help="Sin Claude")
    parser.add_argument("--visible", action="store_true", help="Mostrar navegador")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    args = parser.parse_args()
    
    if not DROPKILLER_EMAIL or not DROPKILLER_PASSWORD:
        print("ERROR: Falta DROPKILLER_EMAIL o DROPKILLER_PASSWORD en .env")
        sys.exit(1)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Falta SUPABASE_URL o SUPABASE_KEY en .env")
        sys.exit(1)
    
    print("=" * 65)
    print(f"  ESTRATEGAS IA - Scraper v4.6 {'(DEBUG)' if args.debug else ''}")
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
            
            print(f"      V7d:{sales7d} V30d:{sales30d} | ${cost:,} | ROI:{margin['roi']}%")
            
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
                print(f"     • {p['name'][:30]} | V7d:{p['sales7d']} V30d:{p['sales30d']} | ${p['cost']:,}")
        
        print("=" * 65)
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
