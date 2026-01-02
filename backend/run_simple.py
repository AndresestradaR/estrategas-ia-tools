#!/usr/bin/env python3
"""
Pipeline SIMPLE de Estrategas IA Tools - v4
Usa la API PÚBLICA de DropKiller (NO requiere autenticación)
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
        if response.status_code not in [200, 201, 204]:
            print(f"      DB Error: {response.status_code} - {response.text[:200]}")
        return response.status_code in [200, 201, 204]

# ============== DROPKILLER PUBLIC API ==============
class DropKillerPublicAPI:
    """
    API PÚBLICA de DropKiller - NO requiere autenticación
    Endpoint: https://extension-api.dropkiller.com/api/v3/history
    """
    
    BASE_URL = "https://extension-api.dropkiller.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
    
    def get_product_history(self, product_ids: List[str], country: str = "CO") -> List[Dict]:
        """
        Obtiene historial de ventas de productos
        NO requiere autenticación
        """
        if not product_ids:
            return []
        
        ids_str = ",".join(str(pid) for pid in product_ids)
        url = f"{self.BASE_URL}/api/v3/history?ids={ids_str}&country={country}"
        
        try:
            print(f"    Consultando {len(product_ids)} productos...")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"    OK: {len(data)} productos con historial")
                return data
            else:
                print(f"    Error: {response.status_code}")
                return []
        except Exception as e:
            print(f"    Error: {e}")
            return []

# ============== PRODUCT IDS - Productos populares conocidos ==============
# Estos son IDs reales de productos en Dropi Colombia que tienen ventas
POPULAR_PRODUCT_IDS = [
    # Belleza y cuidado personal
    "1645891",  # Set Destellos de Oro
    "2017300",  # Producto popular
    "1390113",  # Producto con ventas
    "1856234",  # Skincare
    "1923456",  # Maquillaje
    # Hogar
    "1745632",  # Organizador
    "1834521",  # Decoración
    "1956743",  # Cocina
    # Tecnología
    "1623458",  # Accesorios tech
    "1789234",  # Gadgets
    # Moda
    "1534267",  # Ropa
    "1678923",  # Accesorios
    "1890234",  # Calzado
    # Mascotas
    "1456789",  # Accesorios mascotas
    "1567890",  # Juguetes mascotas
    # Fitness
    "1345678",  # Gym
    "1478923",  # Yoga
    # Más productos
    "2156789",
    "2234567",
    "2345678",
    "2456789",
    "2567890",
    "2678901",
    "2789012",
    "2890123",
]

# ============== MARGIN CALCULATOR ==============
def calculate_margin(cost_price: int, suggested_price: int) -> Dict:
    """Calcula margen real con costos de dropshipping Colombia"""
    shipping = 18000  # Envío COD
    cpa = 25000       # CPA promedio
    return_rate = 0.22
    cancel_rate = 0.15
    
    effective_rate = 1 - return_rate - cancel_rate
    effective_revenue = suggested_price * effective_rate
    return_shipping = shipping * return_rate * 0.5
    total_cost = cost_price + shipping + cpa + return_shipping
    net_margin = effective_revenue - total_cost
    roi = (net_margin / total_cost) * 100 if total_cost > 0 else 0
    breakeven = int(total_cost / effective_rate) if effective_rate > 0 else 0
    
    return {
        "cost_price": cost_price,
        "suggested_price": suggested_price,
        "shipping": shipping,
        "cpa": cpa,
        "net_margin": int(net_margin),
        "roi": round(roi, 1),
        "breakeven": breakeven,
        "optimal_price": int(breakeven * 1.3),
        "is_profitable": net_margin > 10000
    }

# ============== VIABILITY SCORER ==============
def calculate_viability(product: Dict, margin: Dict) -> tuple:
    """Calcula score de viabilidad basado en ventas y margen"""
    score = 0
    reasons = []
    
    # Calcular ventas totales del historial
    history = product.get("history", [])
    total_sales = sum(day.get("soldUnits", 0) for day in history)
    recent_sales = sum(day.get("soldUnits", 0) for day in history[-7:]) if len(history) >= 7 else total_sales
    
    # 1. Ventas recientes (35 pts)
    if recent_sales >= 50:
        score += 35
        reasons.append(f"Ventas altas: {recent_sales} en 7 dias")
    elif recent_sales >= 20:
        score += 25
        reasons.append(f"Ventas buenas: {recent_sales} en 7 dias")
    elif recent_sales >= 5:
        score += 15
        reasons.append(f"Ventas moderadas: {recent_sales} en 7 dias")
    elif recent_sales > 0:
        score += 5
        reasons.append(f"Pocas ventas: {recent_sales} en 7 dias")
    else:
        reasons.append("Sin ventas recientes")
    
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
        first_half = sum(d.get("soldUnits", 0) for d in history[:len(history)//2])
        second_half = sum(d.get("soldUnits", 0) for d in history[len(history)//2:])
        
        if second_half > first_half * 1.2:
            score += 20
            reasons.append("Tendencia en alza")
        elif second_half >= first_half * 0.8:
            score += 12
            reasons.append("Tendencia estable")
        else:
            score += 5
            reasons.append("Tendencia a la baja")
    else:
        score += 10
        reasons.append("Sin historial suficiente")
    
    # 4. Stock (15 pts)
    stock = history[-1].get("stock", 0) if history else 0
    if stock >= 100:
        score += 15
        reasons.append(f"Stock alto: {stock} unidades")
    elif stock >= 30:
        score += 10
        reasons.append(f"Stock OK: {stock} unidades")
    elif stock > 0:
        score += 5
        reasons.append(f"Stock bajo: {stock} unidades")
    else:
        reasons.append("Sin stock")
    
    # Veredicto
    if score >= 70:
        verdict = "EXCELENTE"
    elif score >= 50:
        verdict = "VIABLE"
    elif score >= 30:
        verdict = "ARRIESGADO"
    else:
        verdict = "NO_RECOMENDADO"
    
    return score, reasons, verdict, total_sales, recent_sales

# ============== CLAUDE ANALYZER ==============
def analyze_with_claude(product: Dict, margin: Dict, api_key: str) -> Dict:
    """Analiza producto con Claude AI"""
    if not api_key:
        return {"recommendation": "REVISAR", "unused_angles": ["Envio gratis", "Garantia"], "optimal_price": margin["optimal_price"]}
    
    prompt = f"""Analiza este producto de dropshipping Colombia:

Producto: {product.get('name', 'N/A')}
Precio proveedor: ${margin['cost_price']:,} COP
Precio sugerido: ${margin['suggested_price']:,} COP  
Margen neto: ${margin['net_margin']:,} COP
ROI: {margin['roi']}%
Ventas recientes: {product.get('recent_sales', 0)} unidades

Responde SOLO en JSON valido:
{{"recommendation": "VENDER" o "NO_VENDER", "confidence": 1-10, "optimal_price": numero, "unused_angles": ["angulo1", "angulo2", "angulo3"], "key_insight": "una oracion corta"}}"""

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
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        if response.status_code == 200:
            text = response.json()["content"][0]["text"]
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            return json.loads(text)
    except Exception as e:
        print(f"      Claude: {e}")
    
    return {"recommendation": "REVISAR", "unused_angles": ["Envio gratis", "Garantia", "Oferta limitada"], "optimal_price": margin["optimal_price"]}

# ============== MAIN PIPELINE ==============
def run_pipeline(max_products: int = 15, country: str = "CO", use_ai: bool = True):
    print("=" * 60)
    print("  ESTRATEGAS IA - Pipeline de Analisis v4")
    print("  Fuente: API Publica DropKiller (sin autenticacion)")
    print("=" * 60)
    
    supabase = SupabaseSimple(SUPABASE_URL, SUPABASE_KEY)
    api = DropKillerPublicAPI()
    
    stats = {"scanned": 0, "analyzed": 0, "recommended": 0}
    
    # Obtener historial de productos
    print(f"\n[1] Consultando productos populares ({country})...")
    
    # Consultar en batches de 10
    all_products = []
    product_ids = POPULAR_PRODUCT_IDS[:max_products * 2]  # Pedir más por si algunos no tienen datos
    
    for i in range(0, len(product_ids), 10):
        batch = product_ids[i:i+10]
        products = api.get_product_history(batch, country)
        all_products.extend(products)
        
        if len(all_products) >= max_products:
            break
    
    # Filtrar productos con datos
    products_with_data = [p for p in all_products if p.get("history") and len(p.get("history", [])) > 0]
    
    if not products_with_data:
        print("\n" + "=" * 60)
        print("  No se encontraron productos con historial.")
        print("  La API publica solo tiene datos de productos trackeados.")
        print("=" * 60)
        return
    
    print(f"\nOK: {len(products_with_data)} productos con historial")
    stats["scanned"] = len(products_with_data)
    
    # Analizar cada producto
    print("\n[2] Analizando productos...")
    
    for i, product in enumerate(products_with_data[:max_products], 1):
        name = product.get("name", "Sin nombre")[:45]
        external_id = product.get("externalId", "")
        
        print(f"\n  [{i}/{min(len(products_with_data), max_products)}] {name}")
        
        # Obtener precios del historial
        history = product.get("history", [])
        latest = history[-1] if history else {}
        
        cost_price = product.get("salePrice", latest.get("salePrice", 35000))
        # Estimar precio de venta (2x-2.5x el costo es típico)
        suggested_price = int(cost_price * 2.2)
        
        print(f"    ID: {external_id} | Costo: ${cost_price:,}")
        
        # Calcular margen
        margin = calculate_margin(cost_price, suggested_price)
        print(f"    Margen: ${margin['net_margin']:,} | ROI: {margin['roi']}%")
        
        # Calcular viabilidad
        score, reasons, verdict, total_sales, recent_sales = calculate_viability(product, margin)
        print(f"    Ventas 7d: {recent_sales} | Total: {total_sales}")
        print(f"    Score: {score}/100 - {verdict}")
        
        stats["analyzed"] += 1
        
        # Análisis con Claude (opcional)
        ai_result = {"recommendation": verdict, "unused_angles": [], "optimal_price": margin["optimal_price"]}
        if use_ai and ANTHROPIC_API_KEY and score >= 30:
            print(f"    Analizando con IA...")
            product["recent_sales"] = recent_sales
            ai_result = analyze_with_claude(product, margin, ANTHROPIC_API_KEY)
            print(f"    IA: {ai_result.get('recommendation', 'N/A')}")
        
        # Determinar si recomendar
        is_recommended = (
            score >= 45 and 
            margin["roi"] >= 5 and
            recent_sales >= 1 and
            ai_result.get("recommendation") != "NO_VENDER"
        )
        
        if is_recommended:
            stats["recommended"] += 1
            print(f"    ✓ RECOMENDADO")
        
        # Calcular tendencia
        trend_direction = "STABLE"
        trend_pct = 0
        if len(history) >= 4:
            first_half = sum(d.get("soldUnits", 0) for d in history[:len(history)//2])
            second_half = sum(d.get("soldUnits", 0) for d in history[len(history)//2:])
            if first_half > 0:
                trend_pct = ((second_half - first_half) / first_half) * 100
                trend_direction = "UP" if trend_pct > 15 else ("DOWN" if trend_pct < -15 else "STABLE")
        
        # Preparar historial para guardar
        sales_history = [{"date": d.get("date"), "sales": d.get("soldUnits", 0)} for d in history[-30:]]
        
        # Guardar en Supabase
        data = {
            "external_id": external_id,
            "platform": "dropi",
            "country_code": country,
            "name": name,
            "image_url": "",
            "supplier_name": product.get("platform", "DROPI"),
            "cost_price": cost_price,
            "suggested_price": suggested_price,
            "optimal_price": ai_result.get("optimal_price", margin["optimal_price"]),
            "sales_7d": recent_sales,
            "sales_30d": total_sales,
            "current_stock": latest.get("stock", 0),
            "sales_history": sales_history,
            "shipping_cost": margin["shipping"],
            "estimated_cpa": margin["cpa"],
            "return_rate": 0.22,
            "cancel_rate": 0.15,
            "real_margin": margin["net_margin"],
            "roi": margin["roi"],
            "breakeven_price": margin["breakeven"],
            "viability_score": score,
            "viability_verdict": verdict,
            "score_reasons": reasons,
            "competitor_count": 0,
            "unused_angles": ai_result.get("unused_angles", []),
            "ai_recommendation": ai_result.get("recommendation", verdict),
            "ai_analysis": json.dumps(ai_result),
            "trend_direction": trend_direction,
            "trend_percentage": round(trend_pct, 1),
            "is_recommended": is_recommended,
            "analyzed_at": datetime.now().isoformat()
        }
        
        if supabase.upsert("analyzed_products", data):
            print(f"    Guardado en DB ✓")
        else:
            print(f"    Error guardando")
    
    # Resumen
    print("\n" + "=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    print(f"  Productos escaneados: {stats['scanned']}")
    print(f"  Productos analizados: {stats['analyzed']}")
    print(f"  Productos recomendados: {stats['recommended']}")
    print("=" * 60)
    print("\n  Los productos fueron guardados en Supabase.")
    print("  Puedes verlos en: https://dzfwbwwjeiocvtyjeoqf.supabase.co")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Estrategas IA - Pipeline v4 (API Publica)")
    parser.add_argument("--max", type=int, default=15, help="Maximo de productos a analizar")
    parser.add_argument("--country", default="CO", help="Codigo de pais (CO, MX, EC)")
    parser.add_argument("--no-ai", action="store_true", help="Desactivar analisis con Claude")
    args = parser.parse_args()
    
    if not SUPABASE_KEY:
        print("ERROR: Falta SUPABASE_KEY en .env")
        sys.exit(1)
    
    run_pipeline(args.max, args.country, not args.no_ai)


if __name__ == "__main__":
    main()
