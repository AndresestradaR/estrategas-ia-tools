#!/usr/bin/env python3
"""
Scraper Automático de DropKiller - Estrategas IA v2.1
Debug: guarda HTML para análisis
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
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.browser = None
        self.page = None
    
    async def init_browser(self, headless: bool = True):
        from playwright.async_api import async_playwright
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(60000)
    
    async def login(self) -> bool:
        print("  [1] Iniciando login en DropKiller...")
        
        try:
            print("      Cargando página de login...")
            await self.page.goto('https://app.dropkiller.com/sign-in', wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(5)
            
            print("      Buscando campo de email...")
            email_input = None
            for selector in ['input#identifier-field', 'input[name="identifier"]', 'input[type="email"]']:
                try:
                    email_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if email_input:
                        break
                except:
                    continue
            
            if not email_input:
                print("  [✗] No se encontró campo de email")
                return False
            
            print("      Ingresando email...")
            await email_input.fill(self.email)
            await asyncio.sleep(1)
            
            print("      Buscando campo de contraseña...")
            password_input = None
            for selector in ['input#password-field', 'input[type="password"]']:
                try:
                    password_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if password_input:
                        break
                except:
                    continue
            
            if not password_input:
                print("  [✗] No se encontró campo de contraseña")
                return False
            
            print("      Ingresando contraseña...")
            await password_input.fill(self.password)
            await asyncio.sleep(1)
            
            print("      Enviando formulario...")
            try:
                submit_btn = await self.page.wait_for_selector('button:has-text("Iniciar")', timeout=3000)
                await submit_btn.click()
            except:
                await password_input.press('Enter')
            
            print("      Esperando redirección al dashboard...")
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
            print(f"  [✗] Error en login: {e}")
            return False
    
    async def get_products_from_table(self, country: str = "CO", min_sales: int = 20, max_products: int = 100) -> List[Dict]:
        """Extrae productos directamente de la tabla de DropKiller"""
        print(f"  [2] Navegando a productos (ventas >= {min_sales})...")
        
        country_id = DROPKILLER_COUNTRIES.get(country, DROPKILLER_COUNTRIES["CO"])
        url = f"https://app.dropkiller.com/dashboard/products?platform=dropi&country={country_id}&s7min={min_sales}&stock-min=30&limit=100"
        
        try:
            await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
            print("      Esperando que cargue la tabla...")
            await asyncio.sleep(10)
            
            # Scroll para cargar más productos
            print("      Cargando más productos (scroll)...")
            for i in range(8):
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1.5)
            
            await self.page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(2)
            
            # Guardar HTML y screenshot para debug
            html = await self.page.content()
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            await self.page.screenshot(path='debug_products.png', full_page=True)
            print("      DEBUG: Guardado debug_page.html y debug_products.png")
            
            print("      Extrayendo datos...")
            
            # Método: buscar en todo el texto de la página
            products = await self.page.evaluate('''() => {
                const products = [];
                const seen = new Set();
                
                // Obtener todo el texto visible
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                
                let allText = '';
                while (walker.nextNode()) {
                    allText += walker.currentNode.textContent + ' ';
                }
                
                // Buscar patrones de productos
                // Patrón: ID de 6-7 dígitos cerca de números de ventas
                const segments = document.body.innerText.split(/\\n+/);
                
                let currentProduct = {};
                
                for (const segment of segments) {
                    const text = segment.trim();
                    if (!text) continue;
                    
                    // Buscar ID externo
                    const idMatch = text.match(/^(\\d{6,7})$/);
                    if (idMatch) {
                        if (currentProduct.externalId && (currentProduct.sales7d > 0 || currentProduct.name)) {
                            if (!seen.has(currentProduct.externalId)) {
                                seen.add(currentProduct.externalId);
                                products.push({...currentProduct});
                            }
                        }
                        currentProduct = { externalId: idMatch[1], name: '', sales7d: 0, price: 0, stock: 0 };
                        continue;
                    }
                    
                    // Buscar ventas (número seguido de texto de ventas)
                    const salesMatch = text.match(/^(\\d+)$/);
                    if (salesMatch && currentProduct.externalId && !currentProduct.sales7d) {
                        const num = parseInt(salesMatch[1]);
                        if (num < 10000) {  // Probablemente son ventas, no precio
                            currentProduct.sales7d = num;
                        }
                        continue;
                    }
                    
                    // Buscar precio
                    const priceMatch = text.match(/\\$\\s*([\\d.,]+)/);
                    if (priceMatch && currentProduct.externalId) {
                        currentProduct.price = parseInt(priceMatch[1].replace(/[.,]/g, ''));
                        continue;
                    }
                    
                    // Si es texto largo, probablemente es el nombre
                    if (text.length > 10 && text.length < 100 && !/^[\\d$.,\\s]+$/.test(text) && currentProduct.externalId && !currentProduct.name) {
                        currentProduct.name = text;
                    }
                }
                
                // Agregar último producto
                if (currentProduct.externalId && !seen.has(currentProduct.externalId)) {
                    products.push(currentProduct);
                }
                
                return products;
            }''')
            
            print(f"      Método texto: {len(products)} productos")
            
            # Si no funcionó, intentar con selectores específicos
            if len(products) < 3:
                print("      Intentando con selectores CSS...")
                products2 = await self.page.evaluate('''() => {
                    const products = [];
                    const seen = new Set();
                    
                    // Buscar todos los elementos que parecen cards o filas
                    const elements = document.querySelectorAll('div, tr, li, article');
                    
                    for (const el of elements) {
                        const text = el.innerText || '';
                        if (text.length < 20 || text.length > 500) continue;
                        
                        // Buscar ID de 6-7 dígitos
                        const idMatch = text.match(/\\b(\\d{6,7})\\b/);
                        if (!idMatch) continue;
                        
                        const externalId = idMatch[1];
                        if (seen.has(externalId)) continue;
                        
                        // Buscar ventas
                        const salesMatch = text.match(/(\\d+)\\s*(?:ventas|7d|und|uds)/i);
                        const sales7d = salesMatch ? parseInt(salesMatch[1]) : 0;
                        
                        // Buscar precio
                        const priceMatch = text.match(/\\$\\s*([\\d.,]+)/);
                        const price = priceMatch ? parseInt(priceMatch[1].replace(/[.,]/g, '')) : 0;
                        
                        // Buscar nombre (texto antes del ID o después)
                        const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 5 && l.length < 80);
                        let name = '';
                        for (const line of lines) {
                            if (!/^[\\d$.,\\s]+$/.test(line) && !line.includes('ventas')) {
                                name = line;
                                break;
                            }
                        }
                        
                        if (sales7d > 0 || price > 0) {
                            seen.add(externalId);
                            products.push({
                                externalId,
                                name: name || `Producto ${externalId}`,
                                sales7d,
                                price,
                                stock: 0
                            });
                        }
                    }
                    
                    return products;
                }''')
                
                print(f"      Método CSS: {len(products2)} productos")
                if len(products2) > len(products):
                    products = products2
            
            # Filtrar
            products = [p for p in products if int(p.get('externalId', 0)) > 100000][:max_products]
            
            print(f"  [✓] Extraídos {len(products)} productos")
            
            if products:
                print(f"      Ejemplos:")
                for p in products[:3]:
                    print(f"        - {p}")
            
            return products
            
        except Exception as e:
            print(f"  [✗] Error extrayendo productos: {e}")
            import traceback
            traceback.print_exc()
            return []
    
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
    reasons.append("Tendencia: N/A")
    
    if estimated_stock >= 50:
        score += 15
        reasons.append(f"Stock OK: {estimated_stock}")
    elif estimated_stock > 0:
        score += 8
        reasons.append(f"Stock disponible: {estimated_stock}")
    
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
    parser = argparse.ArgumentParser(description="DropKiller Auto Scraper v2")
    parser.add_argument("--min-sales", type=int, default=20, help="Ventas mínimas 7d")
    parser.add_argument("--max-products", type=int, default=50, help="Máx productos")
    parser.add_argument("--country", default="CO", help="País (CO, MX, EC)")
    parser.add_argument("--no-ai", action="store_true", help="Sin Claude")
    parser.add_argument("--visible", action="store_true", help="Mostrar navegador")
    args = parser.parse_args()
    
    if not DROPKILLER_EMAIL or not DROPKILLER_PASSWORD:
        print("ERROR: Falta DROPKILLER_EMAIL o DROPKILLER_PASSWORD en .env")
        sys.exit(1)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Falta SUPABASE_URL o SUPABASE_KEY en .env")
        sys.exit(1)
    
    print("=" * 65)
    print("  ESTRATEGAS IA - Scraper Automático v2.1")
    print("=" * 65)
    print(f"  País: {args.country} | Ventas mín: {args.min_sales} | Máx: {args.max_products}")
    print("=" * 65)
    
    scraper = DropKillerScraper(DROPKILLER_EMAIL, DROPKILLER_PASSWORD)
    supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
    
    stats = {"scraped": 0, "analyzed": 0, "recommended": 0}
    
    try:
        print("\n[FASE 1] Login en DropKiller")
        await scraper.init_browser(headless=not args.visible)
        
        if not await scraper.login():
            print("\nERROR: No se pudo hacer login")
            return
        
        print("\n[FASE 2] Extrayendo productos de la tabla")
        products = await scraper.get_products_from_table(args.country, args.min_sales, args.max_products)
        
        if not products:
            print("\nNo se encontraron productos.")
            print("Revisa debug_page.html y debug_products.png para ver la estructura.")
            return
        
        stats["scraped"] = len(products)
        
        print(f"\n[FASE 3] Analizando {len(products)} productos...\n")
        
        recommended = []
        
        for i, product in enumerate(products, 1):
            ext_id = product.get("externalId", "")
            name = (product.get("name") or "Sin nombre")[:40]
            cost = product.get("price", 35000)
            sales = product.get("sales7d", 0)
            
            print(f"  [{i}/{len(products)}] {name}")
            
            margin = calculate_margin(cost)
            score, reasons, verdict, recent_sales, stock = calculate_viability(product, margin)
            
            print(f"      Ventas: {sales}/7d | Costo: ${cost:,} | ROI: {margin['roi']}% | Score: {score}")
            
            stats["analyzed"] += 1
            
            ai_result = {"recommendation": verdict, "unused_angles": [], "optimal_price": margin["optimal_price"]}
            if not args.no_ai and ANTHROPIC_API_KEY and score >= 30 and sales >= 5:
                ai_result = analyze_with_claude(product, margin)
            
            is_recommended = score >= 50 and margin["roi"] >= 15 and sales >= 10 and ai_result.get("recommendation") != "NO_VENDER"
            
            if is_recommended:
                stats["recommended"] += 1
                print(f"      ✅ RECOMENDADO")
                recommended.append({"name": name, "sales": sales, "margin": margin["net_margin"], "score": score})
            
            data = {
                "external_id": ext_id,
                "platform": "dropi",
                "country_code": args.country,
                "name": name,
                "cost_price": cost,
                "suggested_price": margin["optimal_price"],
                "optimal_price": ai_result.get("optimal_price", margin["optimal_price"]),
                "sales_7d": sales,
                "sales_30d": sales * 4,
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
        print(f"  Productos scrapeados: {stats['scraped']}")
        print(f"  Productos analizados: {stats['analyzed']}")
        print(f"  Productos recomendados: {stats['recommended']}")
        
        if recommended:
            print(f"\n  🏆 TOP RECOMENDADOS:")
            for p in sorted(recommended, key=lambda x: x["score"], reverse=True)[:10]:
                print(f"     • {p['name'][:35]} | Ventas: {p['sales']}/7d | Margen: ${p['margin']:,}")
        
        print("=" * 65)
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
