#!/usr/bin/env python3
"""
Pipeline SIMPLE de Estrategas IA Tools
Sin dependencia pesada de supabase - usa requests directo
"""

import os
import sys
import json
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

COUNTRIES = {
    "CO": {
        "name": "Colombia",
        "dropkiller_id": "65c75a5f-0c4a-45fb-8c90-5b538805a15a",
        "adskiller_id": "10ba518f-80f3-4b8e-b9ba-1a8b62d40c47",
        "shipping_cost": 18000,
        "avg_cpa": 25000,
    }
}

# ============== SUPABASE CLIENT SIMPLE ==============
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
    
    def insert(self, table: str, data: dict):
        url = f"{self.url}/rest/v1/{table}"
        response = requests.post(url, headers=self.headers, json=data)
        return response.status_code in [200, 201, 204]

# ============== DROPKILLER SCRAPER ==============
class DropKillerScraper:
    BASE_URL = "https://app.dropkiller.com"
    
    def __init__(self, jwt: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {jwt}",
            "Cookie": f"__session={jwt}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
    
    def get_products(self, country_code: str = "CO", limit: int = 50, min_sales: int = 50) -> List[Dict]:
        country = COUNTRIES.get(country_code, COUNTRIES["CO"])
        params = {
            "platform": "dropi",
            "country": country["dropkiller_id"],
            "limit": limit,
            "s7min": min_sales,
            "stock-min": 30,
        }
        try:
            response = self.session.get(f"{self.BASE_URL}/api/products", params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("products", data.get("data", []))
            print(f"Error {response.status_code}: {response.text[:200]}")
            return []
        except Exception as e:
            print(f"Error: {e}")
            return []

# ============== ADSKILLER SCRAPER ==============
class AdskillerScraper:
    BASE_URL = "https://app.dropkiller.com"
    
    def __init__(self, jwt: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {jwt}",
            "Cookie": f"__session={jwt}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
        })
    
    def search_ads(self, search_term: str, country_code: str = "CO", limit: int = 15) -> List[Dict]:
        country = COUNTRIES.get(country_code, COUNTRIES["CO"])
        payload = {
            "platform": "facebook",
            "enabled": True,
            "sortBy": "updated_at",
            "order": "desc",
            "countryId": country["adskiller_id"],
            "search": search_term,
            "limit": limit
        }
        try:
            response = self.session.post(f"{self.BASE_URL}/api/adskiller", json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", {}).get("data", [])
            return []
        except Exception as e:
            print(f"Error ads: {e}")
            return []

# ============== MARGIN CALCULATOR ==============
def calculate_margin(cost_price: int, sale_price: int, shipping: int = 18000, cpa: int = 25000) -> Dict:
    effective_rate = 1 - 0.22 - 0.15  # 22% returns, 15% cancels
    effective_revenue = sale_price * effective_rate
    total_cost = cost_price + shipping + cpa + (shipping * 0.22 * 0.5)
    net_margin = effective_revenue - total_cost
    roi = (net_margin / total_cost) * 100 if total_cost > 0 else 0
    breakeven = int(total_cost / effective_rate) if effective_rate > 0 else 0
    
    return {
        "cost_price": cost_price,
        "sale_price": sale_price,
        "net_margin": int(net_margin),
        "roi": round(roi, 1),
        "breakeven_price": breakeven,
        "optimal_price": int(breakeven * 1.3),
        "is_profitable": net_margin > 10000
    }

# ============== CLAUDE ANALYZER ==============
def analyze_with_claude(product: Dict, margin: Dict, competitors: List[Dict], api_key: str) -> Dict:
    if not api_key:
        return {"recommendation": "REVISAR", "unused_angles": [], "optimal_price": margin["optimal_price"]}
    
    comp_summary = "\n".join([f"- {c.get('page_name', 'N/A')}" for c in competitors[:5]])
    
    prompt = f"""Analiza este producto de dropshipping:

Producto: {product.get('name', 'N/A')}
Precio proveedor: ${margin['cost_price']:,} COP
Precio sugerido: ${margin['sale_price']:,} COP
Margen neto: ${margin['net_margin']:,} COP
ROI: {margin['roi']}%
Competidores: {len(competitors)}
{comp_summary}

Responde SOLO en JSON:
{{"recommendation": "VENDER" o "NO_VENDER", "confidence": 1-10, "optimal_price": numero, "unused_angles": ["angulo1", "angulo2"], "key_insight": "una oracion"}}"""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        if response.status_code == 200:
            text = response.json()["content"][0]["text"]
            # Clean JSON
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            return json.loads(text)
    except Exception as e:
        print(f"    Claude error: {e}")
    
    return {"recommendation": "REVISAR", "unused_angles": [], "optimal_price": margin["optimal_price"]}

# ============== MAIN PIPELINE ==============
def run_pipeline(jwt: str, max_products: int = 10, min_sales: int = 50):
    print("=" * 50)
    print("ESTRATEGAS IA - Pipeline de Analisis")
    print("=" * 50)
    
    supabase = SupabaseSimple(SUPABASE_URL, SUPABASE_KEY)
    dropkiller = DropKillerScraper(jwt)
    adskiller = AdskillerScraper(jwt)
    
    stats = {"scanned": 0, "analyzed": 0, "recommended": 0}
    
    # Get products
    print("\n[1] Obteniendo productos de DropKiller...")
    products = dropkiller.get_products(limit=max_products, min_sales=min_sales)
    
    if not products:
        print("ERROR: No se encontraron productos. JWT expirado?")
        return
    
    print(f"OK: {len(products)} productos encontrados")
    stats["scanned"] = len(products)
    
    # Analyze each
    print("\n[2] Analizando productos...")
    for i, product in enumerate(products, 1):
        name = product.get("name", "Sin nombre")[:40]
        print(f"\n  [{i}/{len(products)}] {name}")
        
        # Get prices
        cost = product.get("salePrice", product.get("price", 0))
        sale = product.get("suggestedPrice", cost * 2)
        
        # Calculate margin
        margin = calculate_margin(cost, sale)
        print(f"    Margen: ${margin['net_margin']:,} | ROI: {margin['roi']}%")
        
        if margin["roi"] < -20:
            print(f"    SKIP - ROI muy bajo")
            continue
        
        # Find competitors
        keywords = " ".join(name.lower().split()[:3])
        competitors = adskiller.search_ads(keywords)
        print(f"    Competidores: {len(competitors)}")
        
        # AI Analysis
        print(f"    Analizando con IA...")
        ai = analyze_with_claude(product, margin, competitors, ANTHROPIC_API_KEY)
        print(f"    IA: {ai.get('recommendation', 'N/A')}")
        
        stats["analyzed"] += 1
        
        # Determine if recommended
        is_recommended = (
            margin["roi"] >= 10 and 
            margin["net_margin"] >= 5000 and 
            ai.get("recommendation") != "NO_VENDER"
        )
        
        if is_recommended:
            stats["recommended"] += 1
            print(f"    ✓ RECOMENDADO")
        
        # Save to Supabase
        data = {
            "external_id": str(product.get("id", product.get("externalId", ""))),
            "platform": "dropi",
            "country_code": "CO",
            "name": name,
            "image_url": product.get("image", product.get("imageUrl", "")),
            "cost_price": margin["cost_price"],
            "suggested_price": margin["sale_price"],
            "optimal_price": ai.get("optimal_price", margin["optimal_price"]),
            "sales_7d": product.get("sales7d", product.get("soldUnits7d", 0)),
            "sales_30d": product.get("sales30d", product.get("soldUnits30d", 0)),
            "current_stock": product.get("stock", 0),
            "real_margin": margin["net_margin"],
            "roi": margin["roi"],
            "breakeven_price": margin["breakeven_price"],
            "viability_score": 60 if is_recommended else 30,
            "viability_verdict": "VIABLE" if is_recommended else "NO_RECOMENDADO",
            "competitor_count": len(competitors),
            "unused_angles": ai.get("unused_angles", []),
            "ai_recommendation": ai.get("recommendation", ""),
            "ai_analysis": json.dumps(ai),
            "is_recommended": is_recommended,
            "analyzed_at": datetime.now().isoformat()
        }
        
        if supabase.upsert("analyzed_products", data):
            print(f"    Guardado en DB")
        else:
            print(f"    Error guardando")
    
    # Summary
    print("\n" + "=" * 50)
    print("RESUMEN")
    print("=" * 50)
    print(f"Escaneados: {stats['scanned']}")
    print(f"Analizados: {stats['analyzed']}")
    print(f"Recomendados: {stats['recommended']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jwt", required=True, help="JWT de DropKiller")
    parser.add_argument("--max", type=int, default=10, help="Max productos")
    parser.add_argument("--min-sales", type=int, default=50, help="Ventas minimas 7d")
    args = parser.parse_args()
    
    if not SUPABASE_KEY:
        print("ERROR: Falta SUPABASE_KEY en .env")
        sys.exit(1)
    
    run_pipeline(args.jwt, args.max, args.min_sales)


if __name__ == "__main__":
    main()
