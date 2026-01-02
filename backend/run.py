#!/usr/bin/env python3
"""
Pipeline principal de Estrategas IA Tools
Ejecuta el analisis completo de productos

Uso:
    python run.py --jwt="tu_token_de_dropkiller"
    
O con variables de entorno:
    export DROPKILLER_JWT="tu_token"
    export ANTHROPIC_API_KEY="tu_key"
    python run.py
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import List, Dict

from supabase import create_client, Client

from config import (
    SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY,
    COUNTRIES, DEFAULT_FILTERS, ANALYSIS_CONFIG
)
from scraper import (
    DropKillerScraper, AdskillerScraper,
    extract_competitor_data, extract_used_angles
)
from analyzer import (
    MarginCalculator, ViabilityScorer, ProductAnalyzer,
    should_recommend_product
)


class Pipeline:
    """Pipeline principal de analisis"""
    
    def __init__(
        self,
        jwt: str,
        anthropic_key: str,
        supabase_url: str,
        supabase_key: str
    ):
        self.jwt = jwt
        self.dropkiller = DropKillerScraper(jwt)
        self.adskiller = AdskillerScraper(jwt)
        self.analyzer = ProductAnalyzer(anthropic_key)
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        self.stats = {
            "started_at": datetime.now().isoformat(),
            "products_scanned": 0,
            "products_analyzed": 0,
            "products_recommended": 0,
            "errors": []
        }
    
    def run(
        self,
        country_code: str = "CO",
        max_products: int = 50,
        min_sales_7d: int = 50
    ):
        """
        Ejecuta el pipeline completo
        """
        print("=" * 60)
        print("ESTRATEGAS IA - Pipeline de Analisis")
        print("=" * 60)
        print(f"Pais: {country_code}")
        print(f"Maximo productos: {max_products}")
        print(f"Ventas minimas 7d: {min_sales_7d}")
        print("=" * 60)
        
        country = COUNTRIES.get(country_code, COUNTRIES["CO"])
        
        # Paso 1: Obtener productos de DropKiller
        print("\n[1] Obteniendo productos de DropKiller...")
        products = self.dropkiller.get_products(
            country_code=country_code,
            min_sales_7d=min_sales_7d,
            min_stock=DEFAULT_FILTERS["min_stock"],
            min_price=DEFAULT_FILTERS["min_price"],
            max_price=DEFAULT_FILTERS["max_price"],
            limit=max_products
        )
        
        if not products:
            print("ERROR: No se encontraron productos. Verifica el JWT.")
            return self.stats
        
        print(f"OK: {len(products)} productos encontrados")
        self.stats["products_scanned"] = len(products)
        
        # Paso 2: Analizar cada producto
        print("\n[2] Analizando productos...")
        
        for i, product in enumerate(products, 1):
            try:
                self._analyze_product(product, country, i, len(products))
            except Exception as e:
                error_msg = f"Error en producto {product.get('id', 'unknown')}: {str(e)}"
                print(f"  ERROR: {error_msg}")
                self.stats["errors"].append(error_msg)
        
        # Resumen final
        print("\n" + "=" * 60)
        print("RESUMEN")
        print("=" * 60)
        print(f"Productos escaneados: {self.stats['products_scanned']}")
        print(f"Productos analizados: {self.stats['products_analyzed']}")
        print(f"Productos recomendados: {self.stats['products_recommended']}")
        print(f"Errores: {len(self.stats['errors'])}")
        
        self._save_run_log()
        
        return self.stats
    
    def _analyze_product(self, product: Dict, country: Dict, index: int, total: int):
        """
        Analiza un producto individual
        """
        product_name = product.get("name", "Sin nombre")[:50]
        product_id = str(product.get("id", product.get("externalId", "")))
        
        print(f"\n  [{index}/{total}] {product_name}...")
        
        cost_price = product.get("salePrice", product.get("price", 0))
        sale_price = product.get("suggestedPrice", product.get("suggested_price", cost_price * 2))
        sales_7d = product.get("sales7d", product.get("soldUnits7d", 0))
        sales_30d = product.get("sales30d", product.get("soldUnits30d", 0))
        stock = product.get("stock", product.get("currentStock", 0))
        
        margin = MarginCalculator.calculate(
            cost_price=cost_price,
            sale_price=sale_price,
            shipping_cost=country["shipping_cost"],
            cpa=country["avg_cpa"],
            return_rate=ANALYSIS_CONFIG["return_rate"],
            cancel_rate=ANALYSIS_CONFIG["cancel_rate"]
        )
        
        print(f"    Margen neto: ${margin['net_margin']:,} | ROI: {margin['roi']}%")
        
        if margin["roi"] < -20:
            print(f"    SKIP - ROI muy bajo ({margin['roi']}%)")
            return
        
        print(f"    Buscando competencia...")
        ads = self.adskiller.find_competitors(product_name, country_code="CO")
        competitors = extract_competitor_data(ads)
        used_angles = extract_used_angles(competitors)
        
        print(f"    {len(competitors)} competidores encontrados")
        
        sales_history = product.get("history", [])
        
        product_data = {
            "name": product_name,
            "sales_7d": sales_7d,
            "sales_30d": sales_30d,
            "stock": stock
        }
        
        score, reasons, verdict = ViabilityScorer.calculate(
            product=product_data,
            margin_data=margin,
            competitors=competitors,
            sales_history=sales_history
        )
        
        print(f"    Score: {score}/100 - {verdict}")
        
        print(f"    Analizando con IA...")
        ai_analysis = self.analyzer.analyze_product(
            product=product_data,
            margin_data=margin,
            competitors=competitors,
            used_angles=used_angles
        )
        
        recommendation = ai_analysis.get("recommendation", "REVISAR")
        print(f"    IA recomienda: {recommendation}")
        
        self.stats["products_analyzed"] += 1
        
        is_recommended = should_recommend_product(score, margin, ai_analysis)
        
        if is_recommended:
            self.stats["products_recommended"] += 1
            print(f"    RECOMENDADO")
        else:
            print(f"    No recomendado")
        
        self._save_to_database(
            product=product,
            margin=margin,
            score=score,
            reasons=reasons,
            verdict=verdict,
            competitors=competitors,
            used_angles=used_angles,
            ai_analysis=ai_analysis,
            is_recommended=is_recommended,
            country_code="CO"
        )
    
    def _save_to_database(
        self,
        product: Dict,
        margin: Dict,
        score: int,
        reasons: List[str],
        verdict: str,
        competitors: List[Dict],
        used_angles: List[str],
        ai_analysis: Dict,
        is_recommended: bool,
        country_code: str
    ):
        """
        Guarda el producto analizado en Supabase
        """
        product_id = str(product.get("id", product.get("externalId", "")))
        
        comp_prices = [c.get("sale_price", 0) for c in competitors if c.get("sale_price")]
        
        data = {
            "external_id": product_id,
            "platform": "dropi",
            "country_code": country_code,
            "name": product.get("name", "")[:255],
            "image_url": product.get("image", product.get("imageUrl", "")),
            "supplier_name": product.get("supplierName", product.get("supplier", "")),
            
            "cost_price": margin["cost_price"],
            "suggested_price": margin["sale_price"],
            "optimal_price": ai_analysis.get("optimal_price", margin["optimal_price"]),
            
            "sales_7d": product.get("sales7d", product.get("soldUnits7d", 0)),
            "sales_30d": product.get("sales30d", product.get("soldUnits30d", 0)),
            "current_stock": product.get("stock", product.get("currentStock", 0)),
            
            "sales_history": product.get("history", []),
            
            "shipping_cost": margin["shipping_cost"],
            "estimated_cpa": margin["cpa"],
            "return_rate": margin["return_rate"],
            "cancel_rate": margin["cancel_rate"],
            "real_margin": margin["net_margin"],
            "roi": margin["roi"],
            "breakeven_price": margin["breakeven_price"],
            
            "viability_score": score,
            "viability_verdict": verdict.split(" - ")[0] if " - " in verdict else verdict,
            "score_reasons": reasons,
            
            "competitors": competitors[:10],
            "competitor_count": len(competitors),
            "avg_competitor_price": int(sum(comp_prices) / len(comp_prices)) if comp_prices else None,
            "min_competitor_price": min(comp_prices) if comp_prices else None,
            "max_competitor_price": max(comp_prices) if comp_prices else None,
            
            "used_angles": used_angles[:15],
            "unused_angles": ai_analysis.get("unused_angles", [])[:10],
            
            "ai_analysis": json.dumps(ai_analysis, ensure_ascii=False),
            "ai_recommendation": ai_analysis.get("recommendation", ""),
            "target_audience": ai_analysis.get("target_audience", {}),
            "emotional_triggers": ai_analysis.get("emotional_triggers", []),
            
            "trend_direction": self._calculate_trend_direction(product.get("history", [])),
            "trend_percentage": self._calculate_trend_percentage(product.get("history", [])),
            
            "is_recommended": is_recommended,
            "analyzed_at": datetime.now().isoformat()
        }
        
        try:
            self.supabase.table("analyzed_products").upsert(
                data,
                on_conflict="external_id,platform,country_code"
            ).execute()
            
        except Exception as e:
            print(f"    DB Error: {e}")
            self.stats["errors"].append(f"DB error: {str(e)}")
    
    def _calculate_trend_direction(self, history: List[Dict]) -> str:
        if not history or len(history) < 2:
            return "STABLE"
        
        first = history[0].get("sales", history[0].get("soldUnits", 0))
        last = history[-1].get("sales", history[-1].get("soldUnits", 0))
        
        if first == 0:
            return "UP" if last > 0 else "STABLE"
        
        change = ((last - first) / first) * 100
        
        if change > 15:
            return "UP"
        elif change < -15:
            return "DOWN"
        return "STABLE"
    
    def _calculate_trend_percentage(self, history: List[Dict]) -> float:
        if not history or len(history) < 2:
            return 0.0
        
        first = history[0].get("sales", history[0].get("soldUnits", 0))
        last = history[-1].get("sales", history[-1].get("soldUnits", 0))
        
        if first == 0:
            return 100.0 if last > 0 else 0.0
        
        return round(((last - first) / first) * 100, 1)
    
    def _save_run_log(self):
        """Guarda log de la ejecucion"""
        try:
            self.supabase.table("pipeline_runs").insert({
                "started_at": self.stats["started_at"],
                "finished_at": datetime.now().isoformat(),
                "status": "completed" if not self.stats["errors"] else "completed_with_errors",
                "products_scanned": self.stats["products_scanned"],
                "products_analyzed": self.stats["products_analyzed"],
                "products_recommended": self.stats["products_recommended"],
                "error_message": "\n".join(self.stats["errors"][:5]) if self.stats["errors"] else None
            }).execute()
        except Exception as e:
            print(f"Warning: No se pudo guardar log: {e}")


def main():
    parser = argparse.ArgumentParser(description="Estrategas IA - Pipeline de Analisis")
    parser.add_argument("--jwt", help="JWT de DropKiller", default=os.getenv("DROPKILLER_JWT"))
    parser.add_argument("--country", help="Codigo de pais", default="CO")
    parser.add_argument("--max", type=int, help="Maximo productos", default=30)
    parser.add_argument("--min-sales", type=int, help="Ventas minimas 7d", default=50)
    
    args = parser.parse_args()
    
    jwt = args.jwt
    if not jwt:
        print("ERROR: Se requiere JWT de DropKiller")
        print("   Usa: python run.py --jwt='tu_token'")
        print("   O:   export DROPKILLER_JWT='tu_token'")
        sys.exit(1)
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY)
    if not anthropic_key:
        print("ERROR: Se requiere ANTHROPIC_API_KEY")
        sys.exit(1)
    
    supabase_url = os.getenv("SUPABASE_URL", SUPABASE_URL)
    supabase_key = os.getenv("SUPABASE_KEY", SUPABASE_KEY)
    
    if not supabase_url or not supabase_key:
        print("ERROR: Se requieren credenciales de Supabase")
        sys.exit(1)
    
    pipeline = Pipeline(
        jwt=jwt,
        anthropic_key=anthropic_key,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    pipeline.run(
        country_code=args.country,
        max_products=args.max,
        min_sales_7d=args.min_sales
    )


if __name__ == "__main__":
    main()
