"""
Analizador de productos con Claude AI
"""
import json
from typing import Dict, List, Optional, Tuple
from anthropic import Anthropic
from config import ANALYSIS_CONFIG, COUNTRIES

class MarginCalculator:
    """Calcula margenes reales considerando todos los costos"""
    
    @staticmethod
    def calculate(
        cost_price: int,
        sale_price: int,
        shipping_cost: int = 18000,
        cpa: int = 25000,
        return_rate: float = 0.22,
        cancel_rate: float = 0.15
    ) -> Dict:
        """
        Calcula el margen REAL considerando:
        - Costo del producto
        - Costo de envio (COD)
        - CPA (costo por adquisicion)
        - Tasa de devoluciones
        - Tasa de cancelaciones
        """
        effective_rate = 1 - return_rate - cancel_rate
        effective_revenue = sale_price * effective_rate
        return_shipping_cost = shipping_cost * return_rate * 0.5
        total_cost = cost_price + shipping_cost + cpa + return_shipping_cost
        net_margin = effective_revenue - total_cost
        roi = (net_margin / total_cost) * 100 if total_cost > 0 else 0
        breakeven = int(total_cost / effective_rate) if effective_rate > 0 else 0
        optimal_price = int(breakeven * 1.3)
        
        return {
            "cost_price": cost_price,
            "sale_price": sale_price,
            "shipping_cost": shipping_cost,
            "cpa": cpa,
            "return_rate": return_rate,
            "cancel_rate": cancel_rate,
            "effective_rate": effective_rate,
            "effective_revenue": int(effective_revenue),
            "total_cost": int(total_cost),
            "net_margin": int(net_margin),
            "roi": round(roi, 1),
            "breakeven_price": breakeven,
            "optimal_price": optimal_price,
            "is_profitable": net_margin > ANALYSIS_CONFIG["min_viable_margin"],
            "margin_per_100_sales": int(net_margin * 100)
        }


class ViabilityScorer:
    """Calcula score de viabilidad del producto"""
    
    @staticmethod
    def calculate(
        product: Dict,
        margin_data: Dict,
        competitors: List[Dict],
        sales_history: List[Dict] = None
    ) -> Tuple[int, List[str], str]:
        """
        Calcula score de viabilidad (0-100) basado en:
        - Rentabilidad (35 puntos)
        - Tendencia de ventas (25 puntos)
        - Nivel de competencia (20 puntos)
        - Demanda validada (10 puntos)
        - Potencial de diferenciacion (10 puntos)
        """
        score = 0
        reasons = []
        
        # 1. RENTABILIDAD (35 puntos)
        roi = margin_data.get("roi", 0)
        net_margin = margin_data.get("net_margin", 0)
        
        if roi >= 40:
            score += 35
            reasons.append(f"ROI excelente: {roi}% - Muy rentable")
        elif roi >= 25:
            score += 28
            reasons.append(f"ROI bueno: {roi}% - Rentable")
        elif roi >= 15:
            score += 20
            reasons.append(f"ROI aceptable: {roi}% - Margen ajustado")
        elif roi > 0:
            score += 10
            reasons.append(f"ROI bajo: {roi}% - Riesgo de perdida")
        else:
            score += 0
            reasons.append(f"ROI negativo: {roi}% - PERDIDA de ${abs(net_margin):,} por venta")
        
        # 2. TENDENCIA DE VENTAS (25 puntos)
        if sales_history and len(sales_history) >= 2:
            first_month = sales_history[0].get("sales", 0)
            last_month = sales_history[-1].get("sales", 0)
            
            if first_month > 0:
                trend_pct = ((last_month - first_month) / first_month) * 100
                
                if trend_pct >= 50:
                    score += 25
                    reasons.append(f"Tendencia excelente: +{trend_pct:.0f}% en {len(sales_history)} meses")
                elif trend_pct >= 20:
                    score += 20
                    reasons.append(f"Tendencia positiva: +{trend_pct:.0f}%")
                elif trend_pct >= 0:
                    score += 12
                    reasons.append(f"Tendencia estable: +{trend_pct:.0f}%")
                elif trend_pct >= -20:
                    score += 5
                    reasons.append(f"Tendencia en descenso leve: {trend_pct:.0f}%")
                else:
                    score += 0
                    reasons.append(f"Producto en declive: {trend_pct:.0f}% - Evitar")
        else:
            score += 10
            reasons.append("Sin historial suficiente para evaluar tendencia")
        
        # 3. NIVEL DE COMPETENCIA (20 puntos)
        num_competitors = len(competitors)
        
        if num_competitors == 0:
            score += 15
            reasons.append("Sin competencia visible - Oportunidad o nicho nuevo")
        elif num_competitors <= 3:
            score += 20
            reasons.append(f"Competencia baja: {num_competitors} competidores - Buena oportunidad")
        elif num_competitors <= 7:
            score += 12
            reasons.append(f"Competencia media: {num_competitors} competidores - Requiere diferenciacion")
        elif num_competitors <= 12:
            score += 6
            reasons.append(f"Competencia alta: {num_competitors} competidores - Dificil destacar")
        else:
            score += 0
            reasons.append(f"Mercado saturado: {num_competitors}+ competidores - No recomendado")
        
        # 4. DEMANDA VALIDADA (10 puntos)
        sales_7d = product.get("sales_7d", 0)
        
        if sales_7d >= 300:
            score += 10
            reasons.append(f"Demanda alta: {sales_7d:,} ventas/semana")
        elif sales_7d >= 100:
            score += 7
            reasons.append(f"Demanda validada: {sales_7d:,} ventas/semana")
        elif sales_7d >= 50:
            score += 4
            reasons.append(f"Demanda moderada: {sales_7d} ventas/semana")
        else:
            score += 2
            reasons.append(f"Demanda baja: {sales_7d} ventas/semana")
        
        # 5. POTENCIAL DE DIFERENCIACION (10 puntos)
        used_angles = set()
        for comp in competitors:
            for angle in comp.get("sales_angles", []):
                used_angles.add(angle.lower() if angle else "")
        
        potential_angles = [
            "envio gratis", "garantia extendida", "devolucion gratis",
            "precio mas bajo", "calidad premium", "resultados garantizados",
            "edicion limitada", "oferta por tiempo limitado", "testimonios reales",
            "recomendado por expertos", "el mas vendido", "nuevo lanzamiento"
        ]
        
        unused_count = sum(1 for a in potential_angles if a not in used_angles)
        
        if unused_count >= 8:
            score += 10
            reasons.append(f"Alto potencial: {unused_count} angulos sin explotar")
        elif unused_count >= 5:
            score += 7
            reasons.append(f"Buen potencial: {unused_count} angulos disponibles")
        elif unused_count >= 3:
            score += 4
            reasons.append(f"Potencial limitado: {unused_count} angulos sin usar")
        else:
            score += 2
            reasons.append("Pocos angulos nuevos disponibles")
        
        # VEREDICTO FINAL
        if score >= 75:
            verdict = "EXCELENTE - Alta probabilidad de exito"
        elif score >= 55:
            verdict = "VIABLE - Requiere buena ejecucion"
        elif score >= 35:
            verdict = "ARRIESGADO - Solo con estrategia diferenciada"
        else:
            verdict = "NO_RECOMENDADO - Alta probabilidad de perdida"
        
        return score, reasons, verdict


class ProductAnalyzer:
    """Analizador principal usando Claude AI"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
    
    def analyze_product(
        self,
        product: Dict,
        margin_data: Dict,
        competitors: List[Dict],
        used_angles: List[str]
    ) -> Dict:
        """
        Analiza un producto con Claude y genera recomendaciones
        """
        competitor_summary = []
        for i, comp in enumerate(competitors[:10], 1):
            competitor_summary.append(
                f"{i}. {comp.get('page_name', 'N/A')} - "
                f"Engagement: {comp.get('engagement_level', 'N/A')} - "
                f"Angulo: {comp.get('main_angle', 'N/A')}"
            )
        
        prompt = f"""Analiza este producto de dropshipping y dame recomendaciones especificas.

## PRODUCTO
- Nombre: {product.get('name', 'N/A')}
- Precio proveedor: ${margin_data.get('cost_price', 0):,} COP
- Precio sugerido: ${margin_data.get('sale_price', 0):,} COP
- Ventas 7 dias: {product.get('sales_7d', 0):,}
- Ventas 30 dias: {product.get('sales_30d', 0):,}
- Stock: {product.get('stock', 0):,}

## ANALISIS FINANCIERO
- Margen neto por venta: ${margin_data.get('net_margin', 0):,} COP
- ROI: {margin_data.get('roi', 0)}%
- Precio breakeven: ${margin_data.get('breakeven_price', 0):,} COP
- Es rentable?: {'Si' if margin_data.get('is_profitable') else 'No'}

## COMPETENCIA ({len(competitors)} competidores encontrados)
{chr(10).join(competitor_summary) if competitor_summary else 'No se encontraron competidores'}

## ANGULOS YA USADOS POR LA COMPETENCIA
{', '.join(used_angles[:10]) if used_angles else 'Ninguno identificado'}

---

Responde en JSON con esta estructura exacta:
{{
    "recommendation": "VENDER" | "NO_VENDER" | "VENDER_CON_CONDICIONES",
    "confidence": 1-10,
    "optimal_price": numero en COP,
    "price_justification": "explicacion breve",
    "unused_angles": ["angulo 1", "angulo 2", ...],
    "target_audience": {{
        "age_range": "25-45",
        "gender": "Mujeres 70%",
        "interests": ["interes 1", "interes 2"],
        "pain_points": ["problema 1", "problema 2"]
    }},
    "emotional_triggers": ["trigger 1", "trigger 2"],
    "key_insight": "insight principal en una oracion",
    "risks": ["riesgo 1", "riesgo 2"],
    "action_items": ["accion 1", "accion 2", "accion 3"]
}}

Solo responde con el JSON, sin texto adicional."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            analysis = json.loads(response_text)
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"Error parseando respuesta de Claude: {e}")
            return self._default_analysis()
        except Exception as e:
            print(f"Error en analisis Claude: {e}")
            return self._default_analysis()
    
    def _default_analysis(self) -> Dict:
        """Analisis por defecto si Claude falla"""
        return {
            "recommendation": "REVISAR_MANUALMENTE",
            "confidence": 5,
            "optimal_price": 0,
            "price_justification": "No se pudo analizar automaticamente",
            "unused_angles": [],
            "target_audience": {},
            "emotional_triggers": [],
            "key_insight": "Requiere analisis manual",
            "risks": ["Analisis automatico no disponible"],
            "action_items": ["Revisar manualmente antes de decidir"]
        }


def should_recommend_product(
    viability_score: int,
    margin_data: Dict,
    ai_analysis: Dict
) -> bool:
    """
    Determina si un producto debe ser recomendado para mostrar
    """
    min_score = 45
    min_roi = 10
    min_margin = 5000
    
    if ai_analysis.get("recommendation") == "NO_VENDER":
        return False
    
    if viability_score < min_score:
        return False
    
    if margin_data.get("roi", 0) < min_roi:
        return False
    
    if margin_data.get("net_margin", 0) < min_margin:
        return False
    
    return True
