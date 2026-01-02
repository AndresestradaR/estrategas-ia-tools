#!/usr/bin/env python3
"""
Pipeline Estrategas IA Tools - v7
Soporta IDs manuales o extracción automática
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

# ============== DROPKILLER PUBLIC API ==============
class DropKillerPublicAPI:
    """API pública - NO requiere autenticación"""
    
    BASE_URL = "https://extension-api.dropkiller.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
    
    def get_history(self, product_ids: List[str], country: str = "CO") -> List[Dict]:
        """Obtiene historial de ventas - NO requiere auth"""
        if not product_ids:
            return []
        
        all_results = []
        
        # Procesar en batches de 10
        for i in range(0, len(product_ids), 10):
            batch = product_ids[i:i+10]
            ids_str = ",".join(str(pid) for pid in batch)
            url = f"{self.BASE_URL}/api/v3/history?ids={ids_str}&country={country}"
            
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        all_results.extend(data)
            except Exception as e:
                print(f"    Error batch {i//10 + 1}: {e}")
        
        return all_results

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
def calculate_viability(product: Dict, margin: Dict) -> tuple:
    score = 0
    reasons = []
    
    history = product.get("history", [])
    total_sales = sum(d.get("soldUnits", 0) for d in history)
    recent_sales = sum(d.get("soldUnits", 0) for d in history[-7:]) if len(history) >= 7 else total_sales
    
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
    stock = history[-1].get("stock", 0) if history else 0
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
        return {"recommendation": "REVISAR", "unused_angles": ["Envio gratis", "Garantia"], "optimal_price": margin["optimal_price"]}
    
    prompt = f"""Analiza este producto dropshipping Colombia:

Producto: {product.get('name', 'N/A')}
Costo: ${margin['cost_price']:,} COP
Precio venta: ${margin['suggested_price']:,} COP
Margen: ${margin['net_margin']:,} COP
ROI: {margin['roi']}%
Ventas 7d: {product.get('recent_sales', 0)}

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
    
    return {"recommendation": "REVISAR", "unused_angles": ["Envio gratis", "Garantia"], "optimal_price": margin["optimal_price"]}

# ============== MAIN PIPELINE ==============
def run_pipeline(product_ids: List[str], country: str = "CO", use_ai: bool = True):
    print("=" * 60)
    print("  ESTRATEGAS IA - Pipeline v7")
    print("=" * 60)
    
    if not product_ids:
        print("\nERROR: No hay IDs de productos")
        return
    
    supabase = SupabaseSimple(SUPABASE_URL, SUPABASE_KEY)
    api = DropKillerPublicAPI()
    
    stats = {"scanned": 0, "analyzed": 0, "recommended": 0}
    
    print(f"\n[1] Consultando {len(product_ids)} productos ({country})...")
    
    products = api.get_history(product_ids, country)
    
    # Filtrar productos con datos
    products_with_data = [p for p in products if p.get("history") and len(p.get("history", [])) > 0]
    
    if not products_with_data:
        print("\n    No se encontraron productos con historial de ventas.")
        print("    Los IDs pueden no estar siendo trackeados por DropKiller.")
        return
    
    print(f"    OK: {len(products_with_data)} productos con historial")
    stats["scanned"] = len(products_with_data)
    
    print(f"\n[2] Analizando productos...")
    
    for i, product in enumerate(products_with_data, 1):
        ext_id = product.get("externalId", "")
        name = (product.get("name") or "Sin nombre")[:45]
        history = product.get("history", [])
        
        print(f"\n  [{i}/{len(products_with_data)}] {name}")
        
        # Precios
        cost = product.get("salePrice", 35000)
        suggested = int(cost * 2.2)
        
        print(f"    ID: {ext_id} | Costo: ${cost:,}")
        
        # Margen
        margin = calculate_margin(cost, suggested)
        print(f"    Margen: ${margin['net_margin']:,} | ROI: {margin['roi']}%")
        
        # Viabilidad
        score, reasons, verdict, total_sales, recent_sales = calculate_viability(product, margin)
        print(f"    Ventas 7d: {recent_sales} | Total: {total_sales}")
        print(f"    Score: {score}/100 - {verdict}")
        
        stats["analyzed"] += 1
        
        # IA
        ai_result = {"recommendation": verdict, "unused_angles": [], "optimal_price": margin["optimal_price"]}
        if use_ai and ANTHROPIC_API_KEY and score >= 30:
            product["recent_sales"] = recent_sales
            ai_result = analyze_with_claude(product, margin, ANTHROPIC_API_KEY)
            print(f"    IA: {ai_result.get('recommendation')}")
        
        # Recomendar?
        is_recommended = score >= 45 and margin["roi"] >= 5 and ai_result.get("recommendation") != "NO_VENDER"
        
        if is_recommended:
            stats["recommended"] += 1
            print(f"    ✓ RECOMENDADO")
        
        # Tendencia
        trend_direction = "STABLE"
        trend_pct = 0
        if len(history) >= 4:
            first = sum(d.get("soldUnits", 0) for d in history[:len(history)//2])
            second = sum(d.get("soldUnits", 0) for d in history[len(history)//2:])
            if first > 0:
                trend_pct = ((second - first) / first) * 100
                trend_direction = "UP" if trend_pct > 15 else ("DOWN" if trend_pct < -15 else "STABLE")
        
        # Stock actual
        current_stock = history[-1].get("stock", 0) if history else 0
        
        # Guardar
        data = {
            "external_id": ext_id,
            "platform": "dropi",
            "country_code": country,
            "name": name,
            "image_url": "",
            "cost_price": cost,
            "suggested_price": suggested,
            "optimal_price": ai_result.get("optimal_price", margin["optimal_price"]),
            "sales_7d": recent_sales,
            "sales_30d": total_sales,
            "current_stock": current_stock,
            "real_margin": margin["net_margin"],
            "roi": margin["roi"],
            "breakeven_price": margin["breakeven"],
            "viability_score": score,
            "viability_verdict": verdict,
            "score_reasons": reasons,
            "unused_angles": ai_result.get("unused_angles", []),
            "ai_recommendation": ai_result.get("recommendation", verdict),
            "ai_analysis": json.dumps(ai_result),
            "trend_direction": trend_direction,
            "trend_percentage": round(trend_pct, 1),
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
    parser = argparse.ArgumentParser(description="Estrategas IA - Pipeline v7")
    parser.add_argument("--ids", required=True, help="IDs de productos separados por coma")
    parser.add_argument("--country", default="CO", help="Pais (CO, MX, EC)")
    parser.add_argument("--no-ai", action="store_true", help="Sin Claude")
    args = parser.parse_args()
    
    if not SUPABASE_KEY:
        print("ERROR: Falta SUPABASE_KEY en .env")
        sys.exit(1)
    
    product_ids = [id.strip() for id in args.ids.split(",") if id.strip()]
    
    run_pipeline(product_ids, args.country, not args.no_ai)


if __name__ == "__main__":
    main()
