#!/usr/bin/env python3
"""
Scraper Automático de DropKiller - Estrategas IA v1.1
Login corregido para Clerk Auth
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
    """Scraper con Playwright para DropKiller"""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.browser = None
        self.page = None
    
    async def init_browser(self, headless: bool = True):
        """Inicializa el navegador"""
        from playwright.async_api import async_playwright
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = await self.context.new_page()
    
    async def login(self) -> bool:
        """Login en DropKiller usando Clerk"""
        print("  [1] Iniciando login en DropKiller...")
        
        try:
            await self.page.goto('https://app.dropkiller.com/sign-in', wait_until='networkidle')
            await asyncio.sleep(3)
            
            # Clerk Auth - Buscar campo de email por diferentes selectores
            email_selectors = [
                'input[name="identifier"]',
                'input[id="identifier-field"]',
                'input[type="email"]',
                'input[placeholder*="correo"]',
                'input[placeholder*="email"]',
                '.cl-formFieldInput[name="identifier"]',
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if email_input:
                        print(f"      Email field: {selector}")
                        break
                except:
                    continue
            
            if not email_input:
                print("  [✗] No se encontró campo de email")
                # Guardar screenshot para debug
                await self.page.screenshot(path="debug_login.png")
                print("      Screenshot guardado: debug_login.png")
                return False
            
            await email_input.fill(self.email)
            await asyncio.sleep(1)
            
            # Buscar campo de contraseña
            password_selectors = [
                'input[name="password"]',
                'input[id="password-field"]',
                'input[type="password"]',
                '.cl-formFieldInput[type="password"]',
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if password_input:
                        print(f"      Password field: {selector}")
                        break
                except:
                    continue
            
            if not password_input:
                print("  [✗] No se encontró campo de contraseña")
                await self.page.screenshot(path="debug_login.png")
                return False
            
            await password_input.fill(self.password)
            await asyncio.sleep(1)
            
            # Buscar botón de submit
            submit_selectors = [
                'button:has-text("Iniciar sesión")',
                'button:has-text("Sign in")',
                'button:has-text("Continue")',
                'button:has-text("Continuar")',
                'button.cl-formButtonPrimary',
                'form button[type="submit"]:visible',
                'button[data-localization-key="formButtonPrimary"]',
            ]
            
            submit_btn = None
            for selector in submit_selectors:
                try:
                    submit_btn = await self.page.wait_for_selector(selector, timeout=2000)
                    if submit_btn and await submit_btn.is_visible():
                        print(f"      Submit button: {selector}")
                        break
                except:
                    continue
            
            if not submit_btn:
                # Intentar con Enter
                print("      Intentando con Enter...")
                await password_input.press('Enter')
            else:
                await submit_btn.click()
            
            # Esperar redirección al dashboard
            print("      Esperando redirección...")
            await self.page.wait_for_url('**/dashboard**', timeout=30000)
            print("  [✓] Login exitoso")
            return True
            
        except Exception as e:
            print(f"  [✗] Error en login: {e}")
            try:
                await self.page.screenshot(path="debug_login.png")
                print("      Screenshot guardado: debug_login.png")
            except:
                pass
            return False
    
    async def get_product_ids(self, country: str = "CO", min_sales: int = 20, max_products: int = 100) -> List[str]:
        """Extrae IDs de productos del dashboard"""
        print(f"  [2] Navegando a productos (ventas >= {min_sales})...")
        
        country_id = DROPKILLER_COUNTRIES.get(country, DROPKILLER_COUNTRIES["CO"])
        
        url = f"https://app.dropkiller.com/dashboard/products?platform=dropi&country={country_id}&s7min={min_sales}&stock-min=30&limit=100"
        
        try:
            await self.page.goto(url, wait_until='networkidle')
            await asyncio.sleep(5)
            
            # Scroll para cargar más productos
            print("      Cargando productos...")
            for i in range(5):
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)
            
            # Extraer IDs del HTML
            html = await self.page.content()
            
            # Buscar números de 6-7 dígitos (IDs de productos Dropi)
            matches = re.findall(r'\b(\d{6,7})\b', html)
            ids = list(set(matches))
            
            # Filtrar IDs válidos (> 100000)
            ids = [id for id in ids if int(id) > 100000][:max_products]
            
            print(f"  [✓] Encontrados {len(ids)} IDs de productos")
            return ids
            
        except Exception as e:
            print(f"  [✗] Error extrayendo productos: {e}")
            return []
    
    async def close(self):
        """Cierra el navegador"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            await self.playwright.stop()


# ============== DROPKILLER PUBLIC API ==============
class DropKillerAPI:
    """API pública para historial de ventas"""
    
    BASE_URL = "https://extension-api.dropkiller.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
    
    def get_history(self, product_ids: List[str], country: str = "CO") -> List[Dict]:
        """Obtiene historial de ventas"""
        if not product_ids:
            return []
        
        all_results = []
        seen_ids = set()
        
        for i in range(0, len(product_ids), 10):
            batch = product_ids[i:i+10]
            ids_str = ",".join(batch)
            url = f"{self.BASE_URL}/api/v3/history?ids={ids_str}&country={country}"
            
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        for item in data:
                            ext_id = item.get("externalId")
                            if ext_id and ext_id not in seen_ids:
                                seen_ids.add(ext_id)
                                all_results.append(item)
            except:
                pass
        
        return all_results


# ============== ANALYZER ==============
def calculate_margin(cost_price: int) -> Dict:
    """Calcula margen para dropshipping COD Colombia"""
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
    """Calcula viabilidad del producto"""
    score = 0
    reasons = []
    
    history = product.get("history", [])
    total_sales = sum(d.get("soldUnits", 0) for d in history)
    recent_sales = sum(d.get("soldUnits", 0) for d in history[-7:]) if len(history) >= 7 else total_sales
    estimated_stock = max(history[-1].get("stock", 0) if history else 0, recent_sales * 2) if recent_sales > 0 else 0
    
    # Ventas (40 pts)
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
    
    # ROI (25 pts)
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
    
    # Tendencia (20 pts)
    if len(history) >= 4:
        first = sum(d.get("soldUnits", 0) for d in history[:len(history)//2])
        second = sum(d.get("soldUnits", 0) for d in history[len(history)//2:])
        if second > first * 1.3:
            score += 20
            reasons.append("📈 Tendencia en alza")
        elif second >= first * 0.85:
            score += 12
            reasons.append("Tendencia estable")
        else:
            score += 5
            reasons.append("📉 Tendencia a la baja")
    else:
        score += 10
    
    # Stock (15 pts)
    if estimated_stock >= 50:
        score += 15
        reasons.append(f"Stock OK")
    elif estimated_stock > 0:
        score += 8
        reasons.append(f"Stock disponible")
    
    verdict = "EXCELENTE" if score >= 70 else "VIABLE" if score >= 50 else "ARRIESGADO" if score >= 30 else "NO_RECOMENDADO"
    
    return score, reasons, verdict, total_sales, recent_sales, estimated_stock


def analyze_with_claude(product: Dict, margin: Dict) -> Dict:
    """Analiza con Claude AI"""
    if not ANTHROPIC_API_KEY:
        return {"recommendation": "REVISAR", "unused_angles": [], "optimal_price": margin["optimal_price"]}
    
    prompt = f"""Analiza este producto dropshipping Colombia:

Producto: {product.get('name', 'N/A')}
Costo: ${margin['cost_price']:,} COP
Precio óptimo: ${margin['optimal_price']:,} COP ({margin['multiplier']}x)
Margen: ${margin['net_margin']:,} COP
ROI: {margin['roi']}%
Ventas 7d: {product.get('recent_sales', 0)}

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
    parser = argparse.ArgumentParser(description="DropKiller Auto Scraper")
    parser.add_argument("--min-sales", type=int, default=20, help="Ventas mínimas 7d")
    parser.add_argument("--max-products", type=int, default=50, help="Máx productos a analizar")
    parser.add_argument("--country", default="CO", help="País (CO, MX, EC)")
    parser.add_argument("--no-ai", action="store_true", help="Sin análisis Claude")
    parser.add_argument("--visible", action="store_true", help="Mostrar navegador")
    args = parser.parse_args()
    
    # Validar config
    if not DROPKILLER_EMAIL or not DROPKILLER_PASSWORD:
        print("ERROR: Falta DROPKILLER_EMAIL o DROPKILLER_PASSWORD en .env")
        sys.exit(1)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Falta SUPABASE_URL o SUPABASE_KEY en .env")
        sys.exit(1)
    
    print("=" * 65)
    print("  ESTRATEGAS IA - Scraper Automático v1.1")
    print("=" * 65)
    print(f"  País: {args.country} | Ventas mín: {args.min_sales} | Máx: {args.max_products}")
    print("=" * 65)
    
    # Inicializar
    scraper = DropKillerScraper(DROPKILLER_EMAIL, DROPKILLER_PASSWORD)
    api = DropKillerAPI()
    supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
    
    stats = {"scraped": 0, "analyzed": 0, "recommended": 0}
    
    try:
        # 1. Iniciar navegador y login
        print("\n[FASE 1] Login en DropKiller")
        await scraper.init_browser(headless=not args.visible)
        
        if not await scraper.login():
            print("ERROR: No se pudo hacer login")
            print("\nPrueba con --visible para ver qué está pasando:")
            print("  python scraper_auto.py --visible --max-products 5")
            return
        
        # 2. Extraer IDs de productos
        print("\n[FASE 2] Extrayendo productos")
        product_ids = await scraper.get_product_ids(args.country, args.min_sales, args.max_products)
        
        if not product_ids:
            print("ERROR: No se encontraron productos")
            return
        
        stats["scraped"] = len(product_ids)
        
        # 3. Obtener historial de ventas
        print(f"\n[FASE 3] Obteniendo historial de {len(product_ids)} productos...")
        products = api.get_history(product_ids, args.country)
        products_with_data = [p for p in products if p.get("history")]
        
        print(f"  [✓] {len(products_with_data)} productos con historial")
        
        # 4. Analizar productos
        print(f"\n[FASE 4] Analizando productos...\n")
        
        recommended = []
        
        for i, product in enumerate(products_with_data, 1):
            ext_id = product.get("externalId", "")
            name = (product.get("name") or "Sin nombre")[:40]
            cost = product.get("salePrice", 35000)
            
            print(f"  [{i}/{len(products_with_data)}] {name}")
            
            margin = calculate_margin(cost)
            score, reasons, verdict, total_sales, recent_sales, stock = calculate_viability(product, margin)
            
            print(f"      Ventas: {recent_sales}/7d | ROI: {margin['roi']}% | Score: {score}")
            
            stats["analyzed"] += 1
            
            # IA
            ai_result = {"recommendation": verdict, "unused_angles": [], "optimal_price": margin["optimal_price"]}
            if not args.no_ai and ANTHROPIC_API_KEY and score >= 30 and recent_sales >= 5:
                product["recent_sales"] = recent_sales
                ai_result = analyze_with_claude(product, margin)
            
            # ¿Recomendar?
            is_recommended = score >= 50 and margin["roi"] >= 15 and recent_sales >= 10 and ai_result.get("recommendation") != "NO_VENDER"
            
            if is_recommended:
                stats["recommended"] += 1
                print(f"      ✅ RECOMENDADO")
                recommended.append({"name": name, "sales": recent_sales, "margin": margin["net_margin"], "score": score})
            
            # Guardar en Supabase
            data = {
                "external_id": ext_id,
                "platform": "dropi",
                "country_code": args.country,
                "name": name,
                "cost_price": cost,
                "suggested_price": margin["optimal_price"],
                "optimal_price": ai_result.get("optimal_price", margin["optimal_price"]),
                "sales_7d": recent_sales,
                "sales_30d": total_sales,
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
        
        # Resumen
        print("\n" + "=" * 65)
        print("  RESUMEN")
        print("=" * 65)
        print(f"  Productos scrapeados: {stats['scraped']}")
        print(f"  Productos analizados: {stats['analyzed']}")
        print(f"  Productos recomendados: {stats['recommended']}")
        
        if recommended:
            print(f"\n  🏆 TOP RECOMENDADOS:")
            for p in sorted(recommended, key=lambda x: x["score"], reverse=True)[:5]:
                print(f"     • {p['name'][:35]} | Ventas: {p['sales']}/7d | Margen: ${p['margin']:,}")
        
        print("=" * 65)
        print(f"  ✓ Completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 65)
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
