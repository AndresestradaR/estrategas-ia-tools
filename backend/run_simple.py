#!/usr/bin/env python3
"""
Pipeline Estrategas IA Tools - v6
Extrae productos automáticamente del dashboard de DropKiller
"""

import os
import sys
import json
import re
import argparse
import requests
from datetime import datetime
from typing import List, Dict

from dotenv import load_dotenv

load_dotenv()

# ============== CONFIG ==============
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://dzfwbwwjeiocvtyjeoqf.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

DROPKILLER_COUNTRIES = {
    "CO": "65c75a5f-0c4a-45fb-8c90-5b538805a15a",
    "MX": "98993bd0-955a-4fa3-9612-c9d4389c44d0",
    "EC": "82811e8b-d17d-4ab9-847a-fa925785d566",
}

# ============== SUPABASE CLIENT ==============
class SupabaseSimple:
    def __init__(self, url: str, key: str):
        self.url = url.rstrip('/')
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
    
    def upsert(self, table: str, data: dict):
        url = f"{self.url}/rest/v1/{table}"
        headers = {**self.headers, "Prefer": "resolution=merge-duplicates"}
        response = requests.post(url, headers=headers, json=data)
        return response.status_code in [200, 201, 204]

# ============== DROPKILLER SCRAPER ==============
class DropKillerScraper:
    """Extrae productos del dashboard de DropKiller parseando el HTML"""
    
    BASE_URL = "https://app.dropkiller.com"
    
    def __init__(self, jwt: str):
        self.jwt = jwt
        self.session = requests.Session()
        self.session.cookies.set("__session", jwt, domain="app.dropkiller.com")
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
        })
    
    def get_products(self, country: str = "CO", min_sales: int = 10, limit: int = 50) -> List[Dict]:
        """
        Obtiene productos del dashboard de DropKiller
        Parsea el HTML para extraer los datos embebidos
        """
        country_id = DROPKILLER_COUNTRIES.get(country, DROPKILLER_COUNTRIES["CO"])
        
        # URL con filtros
        url = f"{self.BASE_URL}/dashboard/products"
        params = {
            "platform": "dropi",
            "country": country_id,
            "s7min": min_sales,
            "stock-min": 30,
            "limit": limit,
        }
        
        print(f"    Cargando dashboard de DropKiller...")
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            print(f"    Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"    Error: {response.status_code}")
                return []
            
            html = response.text
            
            # Método 1: Buscar __NEXT_DATA__
            products = self._extract_from_next_data(html)
            if products:
                return products
            
            # Método 2: Buscar JSON inline en scripts
            products = self._extract_from_scripts(html)
            if products:
                return products
            
            # Método 3: Buscar patrones de productos en el HTML
            products = self._extract_from_html_patterns(html)
            if products:
                return products
            
            print("    No se pudieron extraer productos del HTML")
            return []
            
        except Exception as e:
            print(f"    Error: {e}")
            return []
    
    def _extract_from_next_data(self, html: str) -> List[Dict]:
        """Extrae productos de __NEXT_DATA__ (Next.js)"""
        try:
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                
                # Navegar la estructura de Next.js
                props = data.get("props", {}).get("pageProps", {})
                
                # Buscar productos en diferentes ubicaciones posibles
                products = (
                    props.get("products") or 
                    props.get("initialProducts") or 
                    props.get("data", {}).get("products") or
                    props.get("dehydratedState", {}).get("queries", [{}])[0].get("state", {}).get("data", {}).get("products")
                )
                
                if products and isinstance(products, list):
                    print(f"    Extraidos {len(products)} productos de __NEXT_DATA__")
                    return products
        except Exception as e:
            print(f"    Error parseando __NEXT_DATA__: {e}")
        
        return []
    
    def _extract_from_scripts(self, html: str) -> List[Dict]:
        """Busca JSON de productos en scripts inline"""
        try:
            # Buscar arrays de productos
            patterns = [
                r'"products"\s*:\s*(\[[^\]]+\])',
                r'products\s*=\s*(\[[^\]]+\])',
                r'"data"\s*:\s*\{"products"\s*:\s*(\[[^\]]+\])',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html)
                for match in matches:
                    try:
                        products = json.loads(match)
                        if products and len(products) > 0:
                            print(f"    Extraidos {len(products)} productos de scripts")
                            return products
                    except:
                        continue
        except Exception as e:
            print(f"    Error buscando en scripts: {e}")
        
        return []
    
    def _extract_from_html_patterns(self, html: str) -> List[Dict]:
        """Extrae datos de productos desde patrones HTML"""
        products = []
        
        try:
            # Buscar patrones como data-product-id, data-external-id, etc.
            id_pattern = r'data-(?:product-id|external-id|id)=["\'](\d+)["\']'
            name_pattern = r'<h[23][^>]*>([^<]+)</h[23]>'
            price_pattern = r'\$\s*([\d,]+)'
            
            ids = re.findall(id_pattern, html)
            
            if ids:
                print(f"    Encontrados {len(ids)} IDs de productos en HTML")
                for pid in ids[:50]:
                    products.append({
                        "externalId": pid,
                        "id": pid,
                        "name": f"Producto {pid}",
                    })
                return products
                
        except Exception as e:
            print(f"    Error extrayendo de HTML: {e}")
        
        return []

# ============== DROPKILLER PUBLIC API ==============
class DropKillerPublicAPI:
    """API pública para obtener historial de ventas"""
    
    BASE_URL = "https://extension-api.dropkiller.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        })
    
    def get_history(self, product_ids: List[str], country: str = "CO") -> List[Dict]:
        """Obtiene historial de ventas - NO requiere auth"""
        if not product_ids:
            return []
        
        ids_str = ",".join(str(pid) for pid in product_ids)
        url = f"{self.BASE_URL}/api/v3/history?ids={ids_str}&country={country}"
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                return response.json() if isinstance(response.json(), list) else []
        except:
            pass
        return []

# ============== MARGIN CALCULATOR ==============
def calculate_margin(cost_price: int, suggested_price: int) -> Dict:
    shipping = 18000
    cpa = 25000
    effective_rate = 0.63  # 1 - 0.22 - 0.15
    
    effective_revenue = suggested_price * effective_rate
    total_cost = cost_price + shipping + cpa + (shipping * 0.22 * 0.5)
    net_margin = effective_revenue - total_cost
    roi = (net_margin / total_cost) * 100 if total_cost > 0 else 0
    breakeven = int(total_cost / effective_rate)
    
    return {
        "cost_price": cost_price,
        "suggested_price": suggested_price,
        "net_margin": int(net_margin),
        "roi": round(roi, 1),
        "breakeven": breakeven,
        "optimal_price": int(breakeven * 1.3),
    }

# ============== VIABILITY SCORER ==============
def calculate_viability(product: Dict, margin: Dict, history: List[Dict]) -> tuple:
    score = 0
    reasons = []
    
    total_sales = sum(d.get("soldUnits", 0) for d in history)
    recent_sales = sum(d.get("soldUnits", 0) for d in history[-7:]) if len(history) >= 7 else total_sales
    
    # Ventas desde el producto (si el historial está vacío)
    if total_sales == 0:
        recent_sales = product.get("sales7d", product.get("soldUnits7d", 0))
        total_sales = product.get("sales30d", product.get("soldUnits30d", recent_sales * 4))
    
    # 1. Ventas (35 pts)
    if recent_sales >= 50:
        score += 35
        reasons.append(f"Ventas altas: {recent_sales}/7d")
    elif recent_sales >= 20:
        score += 25
        reasons.append(f"Ventas buenas: {recent_sales}/7d")
    elif recent_sales >= 10:
        score += 18
        reasons.append(f"Ventas moderadas: {recent_sales}/7d")
    elif recent_sales >= 3:
        score += 10
        reasons.append(f"Pocas ventas: {recent_sales}/7d")
    else:
        reasons.append(f"Sin ventas: {recent_sales}/7d")
    
    # 2. ROI (30 pts)
    roi = margin.get("roi", 0)
    if roi >= 30:
        score += 30
        reasons.append(f"ROI excelente: {roi}%")
    elif roi >= 15:
        score += 20
        reasons.append(f"ROI bueno: {roi}%")
    elif roi > 0:
        score += 10
        reasons.append(f"ROI bajo: {roi}%")
    else:
        reasons.append(f"ROI negativo: {roi}%")
    
    # 3. Tendencia (20 pts)
    if len(history) >= 4:
        first = sum(d.get("soldUnits", 0) for d in history[:len(history)//2])
        second = sum(d.get("soldUnits", 0) for d in history[len(history)//2:])
        if second > first * 1.2:
            score += 20
            reasons.append("Tendencia UP")
        elif second >= first * 0.8:
            score += 12
            reasons.append("Tendencia estable")
        else:
            score += 5
            reasons.append("Tendencia DOWN")
    else:
        score += 10
    
    # 4. Stock (15 pts)
    stock = product.get("stock", product.get("currentStock", 0))
    if history:
        stock = history[-1].get("stock", stock)
    
    if stock >= 100:
        score += 15
        reasons.append(f"Stock: {stock}")
    elif stock >= 30:
        score += 10
        reasons.append(f"Stock: {stock}")
    elif stock > 0:
        score += 5
        reasons.append(f"Stock bajo: {stock}")
    
    verdict = "EXCELENTE" if score >= 70 else "VIABLE" if score >= 50 else "ARRIESGADO" if score >= 30 else "NO_RECOMENDADO"
    
    return score, reasons, verdict, total_sales, recent_sales

# ============== CLAUDE ANALYZER ==============
def analyze_with_claude(product: Dict, margin: Dict, api_key: str) -> Dict:
    if not api_key:
        return {"recommendation": "REVISAR", "unused_angles": [], "optimal_price": margin["optimal_price"]}
    
    prompt = f"""Analiza este producto dropshipping Colombia:

Producto: {product.get('name', 'N/A')}
Costo: ${margin['cost_price']:,} COP
Precio venta: ${margin['suggested_price']:,} COP
Margen: ${margin['net_margin']:,} COP
ROI: {margin['roi']}%
Ventas 7d: {product.get('sales_7d', 0)}

JSON solo:
{{"recommendation": "VENDER" o "NO_VENDER", "confidence": 1-10, "optimal_price": numero, "unused_angles": ["angulo1", "angulo2"], "key_insight": "oracion"}}"""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 300, "messages": [{"role": "user", "content": prompt}]},
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

# ============== MAIN PIPELINE ==============
def run_pipeline(jwt: str, country: str = "CO", min_sales: int = 10, max_products: int = 20, use_ai: bool = True):
    print("=" * 60)
    print("  ESTRATEGAS IA - Pipeline v6 (Automatico)")
    print("=" * 60)
    
    supabase = SupabaseSimple(SUPABASE_URL, SUPABASE_KEY)
    scraper = DropKillerScraper(jwt)
    public_api = DropKillerPublicAPI()
    
    stats = {"scanned": 0, "analyzed": 0, "recommended": 0}
    
    # 1. Obtener productos del dashboard
    print(f"\n[1] Extrayendo productos de DropKiller ({country})...")
    print(f"    Filtros: ventas_7d >= {min_sales}, stock >= 30")
    
    products = scraper.get_products(country, min_sales, max_products)
    
    if not products:
        print("\n" + "=" * 60)
        print("  No se pudieron extraer productos.")
        print("\n  El JWT puede haber expirado. Obtén uno nuevo:")
        print("  1. Ve a app.dropkiller.com/dashboard/products")
        print("  2. F12 -> Application -> Cookies -> __session")
        print("  3. Copia y ejecuta inmediatamente")
        print("=" * 60)
        return
    
    print(f"\n    OK: {len(products)} productos extraidos")
    stats["scanned"] = len(products)
    
    # 2. Obtener IDs para consultar historial
    product_ids = []
    for p in products:
        pid = p.get("externalId") or p.get("external_id") or p.get("id")
        if pid:
            product_ids.append(str(pid))
    
    # 3. Obtener historial de ventas (API pública)
    print(f"\n[2] Obteniendo historial de ventas...")
    history_data = {}
    
    for i in range(0, len(product_ids), 10):
        batch = product_ids[i:i+10]
        histories = public_api.get_history(batch, country)
        for h in histories:
            eid = h.get("externalId")
            if eid:
                history_data[eid] = h.get("history", [])
    
    print(f"    OK: Historial para {len(history_data)} productos")
    
    # 4. Analizar productos
    print(f"\n[3] Analizando productos...")
    
    for i, product in enumerate(products[:max_products], 1):
        ext_id = str(product.get("externalId") or product.get("external_id") or product.get("id", ""))
        name = (product.get("name") or product.get("title") or "Sin nombre")[:45]
        
        print(f"\n  [{i}/{min(len(products), max_products)}] {name}")
        
        # Precios
        cost = product.get("salePrice") or product.get("price") or product.get("cost", 35000)
        suggested = product.get("suggestedPrice") or product.get("suggested_price") or int(cost * 2.2)
        
        print(f"    ID: {ext_id} | Costo: ${cost:,}")
        
        # Margen
        margin = calculate_margin(cost, suggested)
        print(f"    Margen: ${margin['net_margin']:,} | ROI: {margin['roi']}%")
        
        # Historial
        history = history_data.get(ext_id, [])
        
        # Viabilidad
        score, reasons, verdict, total_sales, recent_sales = calculate_viability(product, margin, history)
        print(f"    Ventas 7d: {recent_sales} | Score: {score}/100 - {verdict}")
        
        stats["analyzed"] += 1
        
        # IA
        ai_result = {"recommendation": verdict, "unused_angles": [], "optimal_price": margin["optimal_price"]}
        if use_ai and ANTHROPIC_API_KEY and score >= 30:
            product["sales_7d"] = recent_sales
            ai_result = analyze_with_claude(product, margin, ANTHROPIC_API_KEY)
            print(f"    IA: {ai_result.get('recommendation')}")
        
        # Recomendar?
        is_recommended = score >= 45 and margin["roi"] >= 5 and ai_result.get("recommendation") != "NO_VENDER"
        
        if is_recommended:
            stats["recommended"] += 1
            print(f"    ✓ RECOMENDADO")
        
        # Guardar
        data = {
            "external_id": ext_id,
            "platform": "dropi",
            "country_code": country,
            "name": name,
            "image_url": product.get("image") or product.get("imageUrl") or "",
            "cost_price": cost,
            "suggested_price": suggested,
            "optimal_price": ai_result.get("optimal_price", margin["optimal_price"]),
            "sales_7d": recent_sales,
            "sales_30d": total_sales,
            "current_stock": product.get("stock", 0),
            "real_margin": margin["net_margin"],
            "roi": margin["roi"],
            "breakeven_price": margin["breakeven"],
            "viability_score": score,
            "viability_verdict": verdict,
            "score_reasons": reasons,
            "unused_angles": ai_result.get("unused_angles", []),
            "ai_recommendation": ai_result.get("recommendation", verdict),
            "ai_analysis": json.dumps(ai_result),
            "is_recommended": is_recommended,
            "analyzed_at": datetime.now().isoformat()
        }
        
        if supabase.upsert("analyzed_products", data):
            print(f"    Guardado ✓")
    
    # Resumen
    print("\n" + "=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    print(f"  Escaneados: {stats['scanned']}")
    print(f"  Analizados: {stats['analyzed']}")
    print(f"  Recomendados: {stats['recommended']}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Estrategas IA - Pipeline v6")
    parser.add_argument("--jwt", required=True, help="JWT de DropKiller (__session)")
    parser.add_argument("--country", default="CO", help="Pais (CO, MX, EC)")
    parser.add_argument("--min-sales", type=int, default=10, help="Ventas minimas 7d")
    parser.add_argument("--max", type=int, default=20, help="Max productos")
    parser.add_argument("--no-ai", action="store_true", help="Sin Claude")
    args = parser.parse_args()
    
    if not SUPABASE_KEY:
        print("ERROR: Falta SUPABASE_KEY en .env")
        sys.exit(1)
    
    run_pipeline(args.jwt, args.country, args.min_sales, args.max, not args.no_ai)


if __name__ == "__main__":
    main()
