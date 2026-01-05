#!/usr/bin/env python3
"""
Scraper Automático de DropKiller - Estrategas IA v3.0
Intercepta llamadas API internas para obtener datos limpios
"""

import os
import sys
import json
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


# ============== DROPKILLER SCRAPER v3 ==============
class DropKillerScraper:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.browser = None
        self.page = None
        self.captured_products = []
    
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
        
        # Interceptar respuestas de API
        self.page.on("response", self._handle_response)
    
    async def _handle_response(self, response):
        """Captura respuestas de API que contienen productos"""
        url = response.url
        
        # Buscar llamadas a API de productos
        if 'product' in url.lower() and response.status == 200:
            try:
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type:
                    data = await response.json()
                    
                    # Si es una lista o tiene productos
                    if isinstance(data, list) and len(data) > 0:
                        print(f"      [API] Capturados {len(data)} items de {url[:50]}...")
                        self.captured_products.extend(data)
                    elif isinstance(data, dict):
                        if 'products' in data:
                            print(f"      [API] Capturados {len(data['products'])} productos")
                            self.captured_products.extend(data['products'])
                        elif 'data' in data and isinstance(data['data'], list):
                            print(f"      [API] Capturados {len(data['data'])} items")
                            self.captured_products.extend(data['data'])
                        elif 'items' in data:
                            print(f"      [API] Capturados {len(data['items'])} items")
                            self.captured_products.extend(data['items'])
            except:
                pass
    
    async def login(self) -> bool:
        print("  [1] Iniciando login en DropKiller...")
        
        try:
            print("      Cargando página de login...")
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
            
            print("      Ingresando credenciales...")
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
            
            print("      Esperando dashboard...")
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
    
    async def get_products(self, country: str = "CO", min_sales: int = 20, max_products: int = 100) -> List[Dict]:
        """Navega a productos y captura datos de API"""
        print(f"  [2] Navegando a productos (ventas >= {min_sales})...")
        
        self.captured_products = []  # Reset
        
        country_id = DROPKILLER_COUNTRIES.get(country, DROPKILLER_COUNTRIES["CO"])
        url = f"https://app.dropkiller.com/dashboard/products?platform=dropi&country={country_id}&s7min={min_sales}&stock-min=30&limit=100"
        
        try:
            await self.page.goto(url, wait_until='networkidle', timeout=60000)
            print("      Esperando carga de datos...")
            await asyncio.sleep(8)
            
            # Scroll para cargar más
            print("      Scroll para cargar más productos...")
            for i in range(8):
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1.5)
            
            await asyncio.sleep(3)
            
            print(f"      Total capturado via API: {len(self.captured_products)} items")
            
            # Si no capturamos nada via API, intentar extraer del DOM
            if len(self.captured_products) == 0:
                print("      API no capturada, extrayendo del DOM...")
                self.captured_products = await self._extract_from_dom()
            
            # Normalizar y filtrar productos
            products = self._normalize_products(self.captured_products, min_sales)[:max_products]
            
            print(f"  [✓] {len(products)} productos procesados")
            
            if products:
                print(f"      Ejemplos:")
                for p in products[:3]:
                    print(f"        - {p['name'][:35]} | ${p['providerPrice']:,} | V7d:{p['sales7d']}")
            
            return products
            
        except Exception as e:
            print(f"  [✗] Error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _extract_from_dom(self) -> List[Dict]:
        """Extrae productos directamente del DOM como fallback"""
        return await self.page.evaluate('''() => {
            const products = [];
            const rows = document.querySelectorAll('tr');
            
            for (const row of rows) {
                const text = row.innerText || '';
                if (!text.includes('COP') || !text.includes('Stock:')) continue;
                
                // Extraer datos
                const stockMatch = text.match(/Stock:\\s*(\\d+)/i);
                const priceMatches = text.match(/(\\d{1,3}(?:\\.\\d{3})*)\\s*COP/g) || [];
                
                // Buscar nombre (primera línea larga que no sea número)
                const lines = text.split('\\n').map(l => l.trim());
                let name = '';
                for (const line of lines) {
                    if (line.length > 15 && line.length < 80 && 
                        !/^[\\d\\s.,COP$]+$/.test(line) &&
                        !line.includes('Stock:') && !line.includes('Proveedor:')) {
                        name = line;
                        break;
                    }
                }
                
                if (!name || priceMatches.length === 0) continue;
                
                // Buscar números de ventas (después del último COP)
                const afterLastCOP = text.split('COP').pop() || '';
                const numbers = afterLastCOP.match(/\\b(\\d{1,4})\\b/g) || [];
                const salesNums = numbers.map(n => parseInt(n)).filter(n => n > 0 && n < 5000);
                
                products.push({
                    name: name,
                    salePrice: parseInt((priceMatches[0] || '0').replace(/[.\\sCOP]/g, '')),
                    profit: priceMatches.length > 1 ? parseInt(priceMatches[1].replace(/[.\\sCOP]/g, '')) : 0,
                    stock: stockMatch ? parseInt(stockMatch[1]) : 0,
                    soldUnits7d: salesNums.length > 0 ? salesNums[0] : 0,
                    soldUnits30d: salesNums.length > 1 ? salesNums[1] : 0,
                });
            }
            
            return products;
        }''')
    
    def _normalize_products(self, raw_products: List[Dict], min_sales: int) -> List[Dict]:
        """Normaliza productos de diferentes fuentes"""
        products = []
        seen = set()
        
        for p in raw_products:
            # Extraer campos con diferentes nombres posibles
            name = p.get('name') or p.get('title') or p.get('productName') or ''
            if not name or len(name) < 5:
                continue
            
            # Filtrar nombres inválidos (headers, etc)
            name_lower = name.lower()
            skip_words = ['ventas', 'facturación', 'fecha', 'página', 'mostrar', 'filtros', 'buscar']
            if any(w in name_lower for w in skip_words):
                continue
            
            provider_price = (
                p.get('salePrice') or p.get('providerPrice') or 
                p.get('price') or p.get('cost') or 0
            )
            
            sales_7d = (
                p.get('soldUnits7d') or p.get('sales7d') or 
                p.get('sold_units_7d') or p.get('ventas7d') or 0
            )
            
            sales_30d = (
                p.get('soldUnits30d') or p.get('sales30d') or 
                p.get('sold_units_30d') or p.get('ventas30d') or 0
            )
            
            stock = p.get('stock') or p.get('currentStock') or p.get('inventory') or 0
            
            external_id = (
                p.get('externalId') or p.get('external_id') or 
                p.get('id') or p.get('productId') or ''
            )
            
            # Crear ID único
            unique_key = f"{name[:20]}_{provider_price}"
            if unique_key in seen:
                continue
            seen.add(unique_key)
            
            # Filtrar por ventas mínimas
            if sales_7d < min_sales:
                continue
            
            products.append({
                'name': name[:60],
                'providerPrice': int(provider_price) if provider_price else 35000,
                'sales7d': int(sales_7d),
                'sales30d': int(sales_30d),
                'stock': int(stock),
                'externalId': str(external_id) if external_id else unique_key.replace(' ', '_'),
            })
        
        return products
    
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
    parser = argparse.ArgumentParser(description="DropKiller Auto Scraper v3.0")
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
    print("  ESTRATEGAS IA - Scraper Automático v3.0")
    print("  (Intercepta API + DOM fallback)")
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
        
        print("\n[FASE 2] Extrayendo productos")
        products = await scraper.get_products(args.country, args.min_sales, args.max_products)
        
        if not products:
            print("\nNo se encontraron productos.")
            return
        
        stats["scraped"] = len(products)
        
        print(f"\n[FASE 3] Analizando {len(products)} productos...\n")
        
        recommended = []
        
        for i, product in enumerate(products, 1):
            ext_id = product.get("externalId", f"prod_{i}")
            name = (product.get("name") or "Sin nombre")[:40]
            cost = product.get("providerPrice", 35000)
            sales7d = product.get("sales7d", 0)
            sales30d = product.get("sales30d", 0)
            stock = product.get("stock", 0)
            
            print(f"  [{i}/{len(products)}] {name}")
            
            margin = calculate_margin(cost)
            score, reasons, verdict, recent_sales, est_stock = calculate_viability(product, margin)
            
            print(f"      V7d:{sales7d} | V30d:{sales30d} | Costo:${cost:,} | ROI:{margin['roi']}%")
            
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
        print(f"  Productos scrapeados: {stats['scraped']}")
        print(f"  Productos analizados: {stats['analyzed']}")
        print(f"  Productos recomendados: {stats['recommended']}")
        
        if recommended:
            print(f"\n  🏆 TOP 10 RECOMENDADOS:")
            for p in sorted(recommended, key=lambda x: x["sales7d"], reverse=True)[:10]:
                print(f"     • {p['name'][:30]} | V7d:{p['sales7d']} | Costo:${p['cost']:,} | Margen:${p['margin']:,}")
        
        print("=" * 65)
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
