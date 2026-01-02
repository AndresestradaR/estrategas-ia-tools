#!/usr/bin/env python3
"""
Pipeline SIMPLE de Estrategas IA Tools - v3
Usa Adskiller como fuente principal (tiene análisis IA incluido)
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

# IDs de países para Adskiller
ADSKILLER_COUNTRIES = {
    "CO": "10ba518f-80f3-4b8e-b9ba-1a8b62d40c47",
    "MX": "40334494-86fc-4fc0-857a-281816247906",
    "EC": "1be5939b-f5b1-41ea-8546-fc72a7381c9d",
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

# ============== ADSKILLER SCRAPER ==============
class AdskillerScraper:
    """Scraper para Adskiller - Anuncios con análisis IA incluido"""
    
    BASE_URL = "https://app.dropkiller.com"
    
    def __init__(self, jwt: str):
        self.jwt = jwt
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {jwt}",
            "Cookie": f"__session={jwt}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://app.dropkiller.com",
            "Referer": "https://app.dropkiller.com/dashboard/adskiller",
        })
    
    def search_ads(self, search_term: str = "", country_code: str = "CO", platform: str = "facebook", limit: int = 30) -> List[Dict]:
        """
        Busca anuncios en Adskiller
        POST https://app.dropkiller.com/dashboard/adskiller
        """
        country_id = ADSKILLER_COUNTRIES.get(country_code, ADSKILLER_COUNTRIES["CO"])
        
        payload = {
            "platform": platform,
            "enabled": True,
            "sortBy": "updated_at",
            "order": "desc",
            "countryId": country_id,
            "search": search_term,
            "limit": limit
        }
        
        try:
            print(f"    Buscando: '{search_term}' en {platform}...")
            response = self.session.post(
                f"{self.BASE_URL}/dashboard/adskiller",
                json=payload,
                timeout=30
            )
            
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        ads = data.get("data", {}).get("data", [])
                        print(f"    Encontrados: {len(ads)} anuncios")
                        return ads
                except json.JSONDecodeError:
                    # Puede ser HTML, intentar extraer JSON
                    pass
            
            # Si falla, mostrar parte de la respuesta
            print(f"    Respuesta: {response.text[:300]}...")
            
        except Exception as e:
            print(f"    Error: {e}")
        
        return []
    
    def get_trending_products(self, country_code: str = "CO", max_products: int = 20) -> List[Dict]:
        """
        Obtiene productos trending buscando términos populares de dropshipping
        """
        all_ads = []
        
        # Términos de búsqueda para encontrar productos COD/dropshipping
        search_terms = [
            "contraentrega",
            "pago contra entrega", 
            "envío gratis",
            "oferta",
            "promoción",
            ""  # Búsqueda vacía = todos los más recientes
        ]
        
        for term in search_terms:
            if len(all_ads) >= max_products:
                break
                
            ads = self.search_ads(term, country_code, "facebook", limit=15)
            
            for ad in ads:
                # Evitar duplicados por ID
                if not any(a.get("id") == ad.get("id") for a in all_ads):
                    all_ads.append(ad)
                    
                if len(all_ads) >= max_products:
                    break
        
        return all_ads[:max_products]

# ============== EXTRACT PRODUCT FROM AD ==============
def extract_product_from_ad(ad: Dict) -> Dict:
    """
    Extrae información del producto desde un anuncio de Adskiller
    """
    product_analysis = ad.get("productAnalysis", {}) or {}
    marketing = ad.get("marketingIntelligence", {}) or {}
    demographics = ad.get("targetDemographics", [{}])[0] if ad.get("targetDemographics") else {}
    
    # Extraer ángulos de venta
    sales_angles = []
    for angle in ad.get("salesAngles", []):
        if angle and angle.get("angle"):
            sales_angles.append({
                "angle": angle.get("angle"),
                "effectiveness": angle.get("effectiveness_score", 0.5)
            })
    
    # Extraer triggers emocionales
    triggers = []
    for trigger in ad.get("emotionalTriggers", []):
        if trigger and trigger.get("trigger"):
            triggers.append(trigger.get("trigger"))
    
    return {
        "id": ad.get("id"),
        "external_ad_id": ad.get("external_ad_id"),
        "name": product_analysis.get("name", ad.get("page_name", "Producto sin nombre")),
        "brand": product_analysis.get("brand", ""),
        "category": product_analysis.get("category", marketing.get("niche", "")),
        "benefits": product_analysis.get("benefits", []),
        "price": product_analysis.get("price"),
        "image_url": ad.get("images", [""])[0] if ad.get("images") else "",
        "video_url": ad.get("videos", [""])[0] if ad.get("videos") else "",
        "page_name": ad.get("page_name", ""),
        "ad_url": ad.get("url", ""),
        "store_url": ad.get("link", ""),
        "likes": ad.get("likes", 0),
        "comments": ad.get("comments", 0),
        "shares": ad.get("shares", 0),
        "active_days": ad.get("active_time", 0) // 86400 if ad.get("active_time") else 0,
        "platforms": ad.get("platforms", []),
        "niche": marketing.get("niche", ""),
        "sub_niches": marketing.get("sub_niches", []),
        "value_propositions": marketing.get("value_propositions", []),
        "price_tier": marketing.get("price_tier", ""),
        "sales_angles": sales_angles,
        "emotional_triggers": triggers,
        "target_age": demographics.get("age_range", ""),
        "target_gender": demographics.get("gender", ""),
        "target_interests": demographics.get("interests", []),
        "pain_points": demographics.get("pain_points", []),
        "description": ad.get("description", "")[:500],
    }

# ============== MARGIN CALCULATOR ==============
def estimate_margin(product: Dict, base_cost: int = 35000) -> Dict:
    """
    Estima el margen basado en el tier de precio del producto
    """
    price_tier = product.get("price_tier", "mid-range")
    
    # Estimaciones por tier
    tier_prices = {
        "low": {"cost": 25000, "sale": 69900},
        "mid-range": {"cost": 40000, "sale": 99900},
        "high": {"cost": 60000, "sale": 149900},
        "premium": {"cost": 80000, "sale": 199900},
    }
    
    prices = tier_prices.get(price_tier, tier_prices["mid-range"])
    cost = prices["cost"]
    sale = prices["sale"]
    
    # Costos fijos Colombia
    shipping = 18000
    cpa = 25000
    
    effective_rate = 1 - 0.22 - 0.15  # 63% efectivo
    effective_revenue = sale * effective_rate
    total_cost = cost + shipping + cpa + (shipping * 0.22 * 0.5)
    net_margin = effective_revenue - total_cost
    roi = (net_margin / total_cost) * 100 if total_cost > 0 else 0
    
    return {
        "estimated_cost": cost,
        "estimated_sale": sale,
        "net_margin": int(net_margin),
        "roi": round(roi, 1),
        "is_profitable": net_margin > 10000
    }

# ============== VIABILITY SCORER ==============
def calculate_viability(product: Dict, margin: Dict) -> tuple:
    """
    Calcula score de viabilidad del producto
    """
    score = 0
    reasons = []
    
    # 1. Rentabilidad (30 pts)
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
    
    # 2. Engagement (25 pts)
    likes = product.get("likes", 0)
    comments = product.get("comments", 0)
    if likes > 1000 or comments > 100:
        score += 25
        reasons.append(f"Engagement alto: {likes} likes, {comments} comentarios")
    elif likes > 100 or comments > 10:
        score += 15
        reasons.append(f"Engagement medio: {likes} likes")
    else:
        score += 5
        reasons.append("Engagement bajo")
    
    # 3. Tiempo activo (20 pts)
    active_days = product.get("active_days", 0)
    if active_days > 30:
        score += 20
        reasons.append(f"Anuncio estable: {active_days} días activo")
    elif active_days > 7:
        score += 12
        reasons.append(f"Anuncio reciente: {active_days} días")
    else:
        score += 5
        reasons.append("Anuncio muy nuevo")
    
    # 4. Análisis de IA disponible (15 pts)
    if product.get("sales_angles"):
        score += 15
        reasons.append(f"{len(product['sales_angles'])} ángulos de venta identificados")
    else:
        score += 5
        reasons.append("Sin ángulos de venta")
    
    # 5. Información de audiencia (10 pts)
    if product.get("target_interests") or product.get("pain_points"):
        score += 10
        reasons.append("Audiencia objetivo definida")
    
    # Veredicto
    if score >= 70:
        verdict = "EXCELENTE"
    elif score >= 50:
        verdict = "VIABLE"
    elif score >= 30:
        verdict = "ARRIESGADO"
    else:
        verdict = "NO_RECOMENDADO"
    
    return score, reasons, verdict

# ============== MAIN PIPELINE ==============
def run_pipeline(jwt: str, max_products: int = 10, country: str = "CO"):
    print("=" * 55)
    print("  ESTRATEGAS IA - Pipeline de Analisis v3")
    print("  Fuente: Adskiller (anuncios con analisis IA)")
    print("=" * 55)
    
    supabase = SupabaseSimple(SUPABASE_URL, SUPABASE_KEY)
    adskiller = AdskillerScraper(jwt)
    
    stats = {"scanned": 0, "analyzed": 0, "recommended": 0}
    
    # Obtener anuncios trending
    print(f"\n[1] Obteniendo anuncios de Adskiller ({country})...")
    ads = adskiller.get_trending_products(country, max_products)
    
    if not ads:
        print("\n" + "=" * 55)
        print("ERROR: No se encontraron anuncios.")
        print("\nPosibles causas:")
        print("  1. JWT expirado (duran ~60 segundos)")
        print("  2. No tienes suscripcion activa de DropKiller")
        print("\nSolucion:")
        print("  1. Ve a https://app.dropkiller.com/dashboard/adskiller")
        print("  2. Asegurate de que carga la pagina")
        print("  3. F12 -> Application -> Cookies -> __session")
        print("  4. Copia el valor e inmediatamente ejecuta el script")
        print("=" * 55)
        return
    
    print(f"\nOK: {len(ads)} anuncios encontrados")
    stats["scanned"] = len(ads)
    
    # Analizar cada anuncio/producto
    print("\n[2] Analizando productos...")
    
    for i, ad in enumerate(ads, 1):
        # Extraer producto del anuncio
        product = extract_product_from_ad(ad)
        name = product.get("name", "Sin nombre")[:40]
        
        print(f"\n  [{i}/{len(ads)}] {name}")
        print(f"    Pagina: {product.get('page_name', 'N/A')}")
        print(f"    Likes: {product.get('likes', 0)} | Dias activo: {product.get('active_days', 0)}")
        
        # Estimar margen
        margin = estimate_margin(product)
        print(f"    Margen estimado: ${margin['net_margin']:,} | ROI: {margin['roi']}%")
        
        # Calcular viabilidad
        score, reasons, verdict = calculate_viability(product, margin)
        print(f"    Score: {score}/100 - {verdict}")
        
        stats["analyzed"] += 1
        
        is_recommended = score >= 50 and margin["roi"] >= 10
        
        if is_recommended:
            stats["recommended"] += 1
            print(f"    ✓ RECOMENDADO")
        
        # Preparar datos para Supabase
        angles_list = [a["angle"] for a in product.get("sales_angles", [])]
        
        data = {
            "external_id": product.get("id", f"ad_{i}"),
            "platform": "adskiller",
            "country_code": country,
            "name": name,
            "image_url": product.get("image_url", ""),
            "supplier_name": product.get("page_name", ""),
            "cost_price": margin["estimated_cost"],
            "suggested_price": margin["estimated_sale"],
            "optimal_price": margin["estimated_sale"],
            "sales_7d": product.get("likes", 0),  # Usamos likes como proxy
            "sales_30d": product.get("likes", 0) * 4,
            "current_stock": 999,
            "real_margin": margin["net_margin"],
            "roi": margin["roi"],
            "breakeven_price": int(margin["estimated_cost"] / 0.63) + 43000,
            "viability_score": score,
            "viability_verdict": verdict,
            "score_reasons": reasons,
            "competitor_count": 1,
            "used_angles": angles_list,
            "unused_angles": [],
            "ai_recommendation": verdict,
            "ai_analysis": json.dumps({
                "niche": product.get("niche"),
                "value_propositions": product.get("value_propositions"),
                "emotional_triggers": product.get("emotional_triggers"),
                "target_audience": {
                    "age": product.get("target_age"),
                    "gender": product.get("target_gender"),
                    "interests": product.get("target_interests"),
                    "pain_points": product.get("pain_points")
                },
                "ad_url": product.get("ad_url"),
                "store_url": product.get("store_url")
            }),
            "target_audience": {
                "age": product.get("target_age"),
                "gender": product.get("target_gender"),
                "interests": product.get("target_interests")
            },
            "emotional_triggers": product.get("emotional_triggers", []),
            "is_recommended": is_recommended,
            "analyzed_at": datetime.now().isoformat()
        }
        
        if supabase.upsert("analyzed_products", data):
            print(f"    Guardado en DB")
        else:
            print(f"    Error guardando en DB")
    
    # Resumen
    print("\n" + "=" * 55)
    print("  RESUMEN")
    print("=" * 55)
    print(f"  Anuncios escaneados: {stats['scanned']}")
    print(f"  Productos analizados: {stats['analyzed']}")
    print(f"  Productos recomendados: {stats['recommended']}")
    print("=" * 55)


def main():
    parser = argparse.ArgumentParser(description="Estrategas IA - Pipeline v3")
    parser.add_argument("--jwt", required=True, help="JWT de DropKiller (__session cookie)")
    parser.add_argument("--max", type=int, default=10, help="Maximo de productos")
    parser.add_argument("--country", default="CO", help="Codigo de pais (CO, MX, EC)")
    args = parser.parse_args()
    
    if not SUPABASE_KEY:
        print("ERROR: Falta SUPABASE_KEY en .env")
        sys.exit(1)
    
    run_pipeline(args.jwt, args.max, args.country)


if __name__ == "__main__":
    main()
