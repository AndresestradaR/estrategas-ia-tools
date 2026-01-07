#!/usr/bin/env python3
"""
Scraper Automático de DropKiller - Estrategas IA v7.3
FILTROS DUROS DE EXPERTO:
- NUEVO: Historial mínimo 12 semanas con ≥50 ventas CADA UNA
- Ventas mínimas: ≥50/7d (semana actual)
- Días activos: ≥4 de 7
- Caída máxima: -30% WoW
- ROI mínimo: ≥20%
- Descarte automático: PICO_UNICO, VIRAL_MUERTO, APARICION_SUBITA, SIN_DATOS, INCONSISTENTE
"""

import os
import sys
import json
import re
import argparse
import asyncio
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from dotenv import load_dotenv

load_dotenv()

# ============== CONFIG ==============
DROPKILLER_EMAIL = os.getenv("DROPKILLER_EMAIL", "")
DROPKILLER_PASSWORD = os.getenv("DROPKILLER_PASSWORD", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

DROPKILLER_COUNTRIES = {
    "CO": "65c75a5f-0c4a-45fb-8c90-5b538805a15a",
    "MX": "98993bd0-955a-4fa3-9612-c9d4389c44d0", 
    "EC": "82811e8b-d17d-4ab9-847a-fa925785d566",
}

# ============== FILTROS DUROS v7.3 ==============
FILTROS_EXPERTO = {
    # NUEVO: Historial probado
    "min_semanas_con_ventas": 12,   # Mínimo 12 semanas con ≥50 ventas
    "min_ventas_por_semana": 50,    # Cada semana debe tener ≥50 ventas
    
    # Filtros de semana actual
    "min_ventas_7d": 50,            # Mínimo 50 ventas en 7 días
    "min_dias_activos": 4,          # Mínimo 4 de 7 días con ventas
    "max_caida_wow": -30,           # Máxima caída -30% semana a semana
    "min_roi": 20,                  # ROI mínimo 20%
    "max_costo_vs_pvp": 0.40,       # Costo máximo 40% del PVP
    
    # Patrones de descarte automático
    "patrones_descarte": [
        "PICO_UNICO",
        "VIRAL_MUERTO", 
        "APARICION_SUBITA",
        "SIN_DATOS",
        "INCONSISTENTE"
    ]
}


# ============== DATA CLASSES ==============
@dataclass
class WeeklyMetrics:
    """Métricas de una semana específica"""
    week_number: int
    total_sales: int
    days_with_sales: int
    avg_daily: float
    max_daily: int
    min_daily: int
    consistency: float


@dataclass
class TrendAnalysis:
    """Análisis completo de tendencia"""
    weeks: List[WeeklyMetrics]
    total_sold: int
    total_days: int
    week_over_week_growth: List[float]
    pattern: str
    pattern_reason: str
    alerts: List[str]
    score: int
    peak_week: int
    peak_vs_current: float
    # NUEVO: Métricas de historial
    semanas_con_50_ventas: int
    historial_solido: bool


@dataclass
class FiltroResult:
    """Resultado de aplicar filtros"""
    pasa: bool
    razones_descarte: List[str]
    metricas: Dict


@dataclass
class Competitor:
    """Competidor individual"""
    uuid: str
    provider_name: str
    sales_7d: int
    sales_30d: int
    price: int
    stock: int
    trend: Optional[TrendAnalysis] = None


@dataclass
class MarketAnalysis:
    """Análisis de mercado completo"""
    product_name: str
    search_term: str
    total_sales_7d: int = 0
    total_sales_30d: int = 0
    competitor_count: int = 0
    competitors: List[Competitor] = field(default_factory=list)
    market_trend: str = ""
    market_growth_7d: float = 0
    leader_share: float = 0
    verdict: str = ""
    verdict_reason: str = ""


@dataclass
class ProductAnalysis:
    """Análisis completo de un producto"""
    uuid: str
    name: str
    provider_name: str
    category: str
    price: int
    stock: int
    sales_7d: int
    sales_30d: int
    trend: TrendAnalysis
    market: Optional[MarketAnalysis]
    roi: float
    optimal_price: int
    final_score: int
    summary: str
    recommendation: str


# ============== FILTRO EXPERTO v7.3 ==============
class FiltroExperto:
    """
    Aplica filtros duros de experto para seleccionar solo productos 
    que realmente valen la pena testear.
    """
    
    @staticmethod
    def aplicar_filtros(product: Dict, trend: TrendAnalysis, margin: Dict) -> FiltroResult:
        """
        Aplica todos los filtros y retorna si pasa o no con las razones.
        """
        razones = []
        metricas = {}
        
        if not trend or not trend.weeks:
            return FiltroResult(pasa=False, razones_descarte=["Sin datos de tendencia"], metricas={})
        
        w0 = trend.weeks[0] if trend.weeks else None
        
        # ============== FILTRO 0: HISTORIAL MÍNIMO (NUEVO - MÁS IMPORTANTE) ==============
        semanas_con_50 = trend.semanas_con_50_ventas
        min_semanas = FILTROS_EXPERTO["min_semanas_con_ventas"]
        metricas["semanas_con_50_ventas"] = semanas_con_50
        
        if semanas_con_50 < min_semanas:
            razones.append(f"Historial insuficiente: {semanas_con_50}/12 semanas con ≥50 ventas")
        
        # ============== FILTRO 1: Patrón de descarte automático ==============
        if trend.pattern in FILTROS_EXPERTO["patrones_descarte"]:
            razones.append(f"Patrón descartado: {trend.pattern}")
        
        metricas["patron"] = trend.pattern
        
        # ============== FILTRO 2: Ventas mínimas (semana actual) ==============
        ventas_7d = w0.total_sales if w0 else 0
        metricas["ventas_7d"] = ventas_7d
        
        if ventas_7d < FILTROS_EXPERTO["min_ventas_7d"]:
            razones.append(f"Ventas insuficientes: {ventas_7d} < {FILTROS_EXPERTO['min_ventas_7d']}")
        
        # ============== FILTRO 3: Días activos ==============
        dias_activos = w0.days_with_sales if w0 else 0
        metricas["dias_activos"] = dias_activos
        
        if dias_activos < FILTROS_EXPERTO["min_dias_activos"]:
            razones.append(f"Inconsistente: {dias_activos}/7 días < {FILTROS_EXPERTO['min_dias_activos']}/7")
        
        # ============== FILTRO 4: Caída WoW ==============
        caida_wow = trend.week_over_week_growth[0] if trend.week_over_week_growth else 0
        metricas["caida_wow"] = caida_wow
        
        if caida_wow < FILTROS_EXPERTO["max_caida_wow"]:
            razones.append(f"Cayendo fuerte: {caida_wow:.0f}% < {FILTROS_EXPERTO['max_caida_wow']}%")
        
        # ============== FILTRO 5: ROI mínimo ==============
        roi = margin.get("roi", 0)
        metricas["roi"] = roi
        
        if roi < FILTROS_EXPERTO["min_roi"]:
            razones.append(f"ROI bajo: {roi:.1f}% < {FILTROS_EXPERTO['min_roi']}%")
        
        # ============== FILTRO 6: Costo vs PVP ==============
        costo = product.get("providerPrice", 0)
        pvp = margin.get("optimal_price", 0)
        ratio_costo = (costo / pvp) if pvp > 0 else 1
        metricas["ratio_costo_pvp"] = ratio_costo
        
        if ratio_costo > FILTROS_EXPERTO["max_costo_vs_pvp"]:
            razones.append(f"Costo alto: {ratio_costo*100:.0f}% > {FILTROS_EXPERTO['max_costo_vs_pvp']*100:.0f}% del PVP")
        
        # ============== RESULTADO ==============
        pasa = len(razones) == 0
        
        return FiltroResult(
            pasa=pasa,
            razones_descarte=razones,
            metricas=metricas
        )
    
    @staticmethod
    def resumen_filtros(productos_analizados: List[Dict]) -> Dict:
        """
        Genera resumen de cuántos productos pasaron/fallaron cada filtro.
        """
        stats = {
            "total_analizados": len(productos_analizados),
            "pasaron": 0,
            "descartados": 0,
            "razones": defaultdict(int)
        }
        
        for p in productos_analizados:
            filtro = p.get("filtro_result")
            if filtro:
                if filtro.pasa:
                    stats["pasaron"] += 1
                else:
                    stats["descartados"] += 1
                    for razon in filtro.razones_descarte:
                        # Extraer categoría principal
                        if "Historial" in razon:
                            stats["razones"]["Sin historial 12 sem"] += 1
                        elif "Patrón" in razon:
                            stats["razones"]["Patrón malo"] += 1
                        elif "Ventas" in razon:
                            stats["razones"]["Pocas ventas"] += 1
                        elif "Inconsistente" in razon:
                            stats["razones"]["Inconsistente"] += 1
                        elif "Cayendo" in razon:
                            stats["razones"]["Cayendo fuerte"] += 1
                        elif "ROI" in razon:
                            stats["razones"]["ROI bajo"] += 1
                        elif "Costo" in razon:
                            stats["razones"]["Costo alto"] += 1
                        else:
                            stats["razones"]["Otros"] += 1
        
        return stats


# ============== TREND ANALYZER v3 - 12 SEMANAS ==============
class TrendAnalyzerV2:
    """
    Analizador de tendencias basado en comparación de ventanas semanales.
    ACTUALIZADO: Analiza 12 semanas completas para validar historial.
    """
    
    @staticmethod
    def analyze(history: List[Dict], created_at: str = None) -> TrendAnalysis:
        if not history:
            return TrendAnalyzerV2._empty_analysis("Sin datos históricos")
        
        sorted_history = sorted(history, key=lambda x: x.get('date', ''), reverse=True)
        daily_sales = [d.get('soldUnits', 0) for d in sorted_history]
        
        if not daily_sales or sum(daily_sales) == 0:
            return TrendAnalyzerV2._empty_analysis("Sin ventas registradas")
        
        # Dividir en 12 semanas (3 meses)
        weeks = []
        for week_num in range(12):
            start_idx = week_num * 7
            end_idx = start_idx + 7
            week_sales = daily_sales[start_idx:end_idx] if start_idx < len(daily_sales) else []
            
            if week_sales and len(week_sales) >= 5:  # Al menos 5 días de datos
                weeks.append(TrendAnalyzerV2._calculate_week_metrics(week_num, week_sales))
            else:
                weeks.append(WeeklyMetrics(
                    week_number=week_num, total_sales=0, days_with_sales=0,
                    avg_daily=0, max_daily=0, min_daily=0, consistency=0
                ))
        
        # ============== CONTAR SEMANAS CON ≥50 VENTAS ==============
        min_ventas = FILTROS_EXPERTO["min_ventas_por_semana"]
        semanas_con_50_ventas = sum(1 for w in weeks if w.total_sales >= min_ventas)
        historial_solido = semanas_con_50_ventas >= FILTROS_EXPERTO["min_semanas_con_ventas"]
        
        # Calcular crecimiento WoW (primeras 4 semanas)
        wow_growth = []
        for i in range(min(len(weeks) - 1, 3)):
            current = weeks[i].total_sales
            previous = weeks[i + 1].total_sales
            if previous > 0:
                growth = ((current - previous) / previous) * 100
            else:
                growth = 100 if current > 0 else 0
            wow_growth.append(round(growth, 1))
        
        # Detectar pico (en todas las semanas)
        week_totals = [w.total_sales for w in weeks]
        max_sales = max(week_totals) if week_totals else 0
        peak_week = week_totals.index(max_sales) if max_sales > 0 else 0
        current_sales = weeks[0].total_sales if weeks else 0
        peak_vs_current = (max_sales / current_sales) if current_sales > 0 else float('inf')
        
        # Detectar patrón
        pattern, pattern_reason, alerts, score = TrendAnalyzerV2._detect_pattern(
            weeks, wow_growth, peak_week, peak_vs_current, daily_sales, semanas_con_50_ventas
        )
        
        return TrendAnalysis(
            weeks=weeks,
            total_sold=sum(daily_sales),
            total_days=len(daily_sales),
            week_over_week_growth=wow_growth,
            pattern=pattern,
            pattern_reason=pattern_reason,
            alerts=alerts,
            score=score,
            peak_week=peak_week,
            peak_vs_current=round(peak_vs_current, 2),
            semanas_con_50_ventas=semanas_con_50_ventas,
            historial_solido=historial_solido
        )
    
    @staticmethod
    def _calculate_week_metrics(week_num: int, sales: List[int]) -> WeeklyMetrics:
        total = sum(sales)
        days_active = len([s for s in sales if s > 0])
        
        return WeeklyMetrics(
            week_number=week_num,
            total_sales=total,
            days_with_sales=days_active,
            avg_daily=round(total / len(sales), 1) if sales else 0,
            max_daily=max(sales) if sales else 0,
            min_daily=min(sales) if sales else 0,
            consistency=round((days_active / len(sales)) * 100, 1) if sales else 0
        )
    
    @staticmethod
    def _detect_pattern(weeks: List[WeeklyMetrics], wow_growth: List[float], 
                        peak_week: int, peak_vs_current: float,
                        daily_sales: List[int], semanas_con_50: int) -> Tuple[str, str, List[str], int]:
        alerts = []
        
        if not weeks or weeks[0].total_sales == 0:
            return "SIN_DATOS", "No hay ventas en la última semana", ["❌ Producto sin actividad reciente"], 0
        
        w0 = weeks[0]
        w1 = weeks[1] if len(weeks) > 1 else None
        w2 = weeks[2] if len(weeks) > 2 else None
        
        # Agregar alerta de historial
        if semanas_con_50 < 12:
            alerts.append(f"⚠️ Solo {semanas_con_50}/12 semanas con ≥50 ventas")
        else:
            alerts.append(f"✅ Historial sólido: {semanas_con_50} semanas con ≥50 ventas")
        
        # APARICIÓN SÚBITA
        if w1 and w2:
            prev_weeks_sales = (w1.total_sales + w2.total_sales)
            if prev_weeks_sales <= 5 and w0.total_sales > 20:
                alerts.append(f"🆕 Sin historial previo (Sem-1: {w1.total_sales}, Sem-2: {w2.total_sales})")
                return (
                    "APARICION_SUBITA",
                    f"Apareció esta semana sin historial previo ({w0.total_sales} ventas vs {prev_weeks_sales} en 2 sem anteriores)",
                    alerts, 45
                )
        
        # VIRAL MUERTO
        if peak_week > 0 and peak_vs_current > 2.5:
            peak_sales = weeks[peak_week].total_sales
            alerts.append(f"🚨 Pico en semana -{peak_week} ({peak_sales} ventas)")
            alerts.append(f"🚨 Actual es {int(100/peak_vs_current)}% del pico")
            return (
                "VIRAL_MUERTO", 
                f"Tuvo pico hace {peak_week} semana(s), ahora está en {int(100/peak_vs_current)}% de ese nivel",
                alerts, max(10, 40 - (peak_week * 10))
            )
        
        # PICO ÚNICO
        if daily_sales:
            max_day = max(daily_sales[:14])
            total_14d = sum(daily_sales[:14])
            if total_14d > 0:
                max_day_ratio = (max_day / total_14d) * 100
                if max_day_ratio > 50:
                    alerts.append(f"🚨 Un día tuvo {max_day_ratio:.0f}% de las ventas de 14 días")
                    return (
                        "PICO_UNICO",
                        f"Un solo día concentró {max_day_ratio:.0f}% de las ventas",
                        alerts, 25
                    )
        
        # DESPEGANDO
        if w1 and w2:
            has_history = w1.total_sales > 10 or w2.total_sales > 10
            if has_history and wow_growth and wow_growth[0] > 20 and (len(wow_growth) < 2 or wow_growth[1] > 0):
                if w0.consistency >= 50:
                    alerts.append(f"✅ Crecimiento: +{wow_growth[0]:.0f}% vs semana anterior")
                    alerts.append(f"✅ Activo {w0.days_with_sales}/7 días")
                    score = min(95, 70 + int(wow_growth[0] / 5) + int(w0.consistency / 10))
                    return (
                        "DESPEGANDO",
                        f"Crecimiento +{wow_growth[0]:.0f}% sostenido, {w0.days_with_sales}/7 días activos",
                        alerts, score
                    )
        
        # CRECIMIENTO SOSTENIDO
        if w1 and wow_growth:
            has_history = w1.total_sales > 10
            if has_history and wow_growth[0] > 10 and w0.consistency >= 40:
                alerts.append(f"✅ Creciendo: +{wow_growth[0]:.0f}%")
                score = min(85, 60 + int(wow_growth[0] / 3))
                return (
                    "CRECIMIENTO_SOSTENIDO",
                    f"Crecimiento +{wow_growth[0]:.0f}%, buena consistencia",
                    alerts, score
                )
        
        # ESTABLE
        if w1 and wow_growth:
            if abs(wow_growth[0]) <= 20 and w0.consistency >= 40:
                alerts.append(f"📊 Variación: {wow_growth[0]:+.0f}%")
                alerts.append(f"📊 Consistencia: {w0.consistency:.0f}%")
                score = 55 + int(w0.consistency / 5)
                return (
                    "ESTABLE",
                    f"Ventas estables ({wow_growth[0]:+.0f}%), consistencia {w0.consistency:.0f}%",
                    alerts, score
                )
        
        # DECAYENDO
        if w1 and wow_growth:
            if wow_growth[0] < -20:
                alerts.append(f"📉 Cayendo: {wow_growth[0]:.0f}%")
                score = max(20, 50 + int(wow_growth[0] / 2))
                return (
                    "DECAYENDO",
                    f"Caída de {abs(wow_growth[0]):.0f}% vs semana anterior",
                    alerts, score
                )
        
        # INCONSISTENTE
        if w0.consistency < 30:
            alerts.append(f"⚠️ Solo {w0.days_with_sales}/7 días con ventas")
            return (
                "INCONSISTENTE",
                f"Solo vende {w0.days_with_sales} días de 7",
                alerts, 35
            )
        
        # DEFAULT
        score = 50 + int(w0.consistency / 4)
        return ("EVALUAR", "Patrón no claro, requiere análisis manual", alerts, score)
    
    @staticmethod
    def _empty_analysis(reason: str) -> TrendAnalysis:
        return TrendAnalysis(
            weeks=[], total_sold=0, total_days=0, week_over_week_growth=[],
            pattern="SIN_DATOS", pattern_reason=reason, alerts=["❌ " + reason],
            score=0, peak_week=0, peak_vs_current=0,
            semanas_con_50_ventas=0, historial_solido=False
        )


# ============== MARKET ANALYZER ==============
class MarketAnalyzer:
    @staticmethod
    def analyze_market(competitors: List[Competitor], product_name: str) -> MarketAnalysis:
        if not competitors:
            return MarketAnalysis(
                product_name=product_name, search_term=product_name,
                verdict="SIN_DATOS", verdict_reason="No se encontraron competidores"
            )
        
        active_competitors = [c for c in competitors if c.sales_7d > 0]
        total_sales_7d = sum(c.sales_7d for c in competitors)
        total_sales_30d = sum(c.sales_30d for c in competitors)
        
        for comp in competitors:
            comp.market_share = (comp.sales_7d / total_sales_7d * 100) if total_sales_7d > 0 else 0
        
        competitors.sort(key=lambda x: x.sales_7d, reverse=True)
        
        if total_sales_30d > 0:
            market_growth = ((total_sales_7d * 4.28) - total_sales_30d) / total_sales_30d * 100
        else:
            market_growth = 0
        
        if market_growth > 15:
            market_trend = "CRECIENDO"
        elif market_growth < -15:
            market_trend = "DECAYENDO"
        else:
            market_trend = "ESTABLE"
        
        leader_share = competitors[0].market_share if competitors else 0
        verdict, reason = MarketAnalyzer._generate_verdict(
            len(active_competitors), total_sales_7d, market_growth, leader_share
        )
        
        return MarketAnalysis(
            product_name=product_name, search_term=product_name,
            total_sales_7d=total_sales_7d, total_sales_30d=total_sales_30d,
            competitor_count=len(active_competitors), competitors=competitors,
            market_trend=market_trend, market_growth_7d=round(market_growth, 1),
            leader_share=round(leader_share, 1), verdict=verdict, verdict_reason=reason
        )
    
    @staticmethod
    def _generate_verdict(num_competitors: int, total_sales: int, growth: float, 
                          leader_share: float) -> Tuple[str, str]:
        if growth < -40:
            return "DECAYENDO", f"Mercado cayendo {growth:.0f}%"
        if num_competitors <= 2:
            return "OPORTUNIDAD_ALTA", f"Solo {num_competitors} competidor(es)"
        if num_competitors <= 4:
            if growth > 10:
                return "OPORTUNIDAD_ALTA", f"{num_competitors} competidores, creciendo"
            return "OPORTUNIDAD_MEDIA", f"{num_competitors} competidores"
        if num_competitors <= 7:
            if leader_share > 50:
                return "DOMINADO", f"Líder tiene {leader_share:.0f}%"
            return "OPORTUNIDAD_MEDIA" if growth > 0 else "SATURADO", f"{num_competitors} competidores"
        return "SATURADO", f"{num_competitors}+ competidores"


# ============== MARGIN CALCULATOR ==============
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
    }


# ============== DROPKILLER SCRAPER v7.3 ==============
class DropKillerScraper:
    def __init__(self, email: str, password: str, debug: bool = False):
        self.email = email
        self.password = password
        self.browser = None
        self.page = None
        self.debug = debug
        self.session_cookies = None
    
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
    
    async def login(self) -> bool:
        print("  [1] Iniciando login...")
        try:
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
            
            try:
                await self.page.wait_for_url('**/dashboard**', timeout=30000)
                print("  [✓] Login exitoso")
                self.session_cookies = await self.context.cookies()
                return True
            except:
                if '/dashboard' in self.page.url:
                    print("  [✓] Login exitoso")
                    self.session_cookies = await self.context.cookies()
                    return True
                return False
        except Exception as e:
            print(f"  [✗] Error: {e}")
            return False
    
    async def extract_products_with_uuid(self) -> List[Dict]:
        return await self.page.evaluate('''() => {
            const products = [];
            const seen = new Set();
            
            const buttons = Array.from(document.querySelectorAll('button')).filter(b => 
                b.innerText && b.innerText.includes('Ver detalle')
            );
            
            for (const btn of buttons) {
                let row = btn.parentElement;
                for (let i = 0; i < 6 && row; i++) {
                    const text = row.innerText || '';
                    if (text.includes('Stock:') && text.includes('COP')) break;
                    row = row.parentElement;
                }
                
                if (!row) continue;
                
                const html = row.innerHTML || '';
                const uuidMatches = html.match(/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/g);
                const uniqueUuids = [...new Set(uuidMatches || [])];
                
                if (uniqueUuids.length === 0) continue;
                const uuid = uniqueUuids[0];
                
                const text = row.innerText || '';
                const lines = text.split('\\n').map(l => l.trim()).filter(l => l);
                
                const stockMatch = text.match(/Stock:\\s*([\\d.,]+)/i);
                const stock = stockMatch ? parseInt(stockMatch[1].replace(/[.,]/g, '')) : 0;
                
                const copIndices = [];
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i].includes('COP')) copIndices.push(i);
                }
                
                if (copIndices.length < 4) continue;
                
                const extractPrice = (line) => {
                    const match = line.match(/([\\d.]+)\\s*COP/);
                    return match ? parseInt(match[1].replace(/\\./g, '')) : 0;
                };
                
                const providerPrice = extractPrice(lines[copIndices[0]]);
                const profit = extractPrice(lines[copIndices[1]]);
                
                let sales7d = 0, sales30d = 0;
                const salesStartIndex = copIndices[1] + 1;
                const salesEndIndex = copIndices[2];
                
                const salesLines = [];
                for (let i = salesStartIndex; i < salesEndIndex; i++) {
                    const cleaned = lines[i].replace(/\\./g, '');
                    if (/^\\d+$/.test(cleaned)) salesLines.push(parseInt(cleaned));
                }
                
                if (salesLines.length >= 1) sales7d = salesLines[0];
                if (salesLines.length >= 2) sales30d = salesLines[1];
                
                let name = '';
                for (const line of lines) {
                    if (/^\\d{1,2}[\\/-]\\d{1,2}[\\/-]\\d{2,4}$/.test(line)) continue;
                    if (/^[\\d.,\\s]+$/.test(line)) continue;
                    if (/COP/.test(line)) continue;
                    if (line.startsWith('Stock:') || line.startsWith('Proveedor:')) continue;
                    if (line.includes('Ver detalle') || line === 'ID') continue;
                    if (/^(Ventas|Facturación|Fecha|Página|Mostrar)/i.test(line)) continue;
                    if (line.length < 5 || line.length > 80) continue;
                    
                    const lower = line.toLowerCase();
                    const skipWords = ['shop', 'store', 'tienda', 'import', 'mayor', 'group', 
                                       'china', 'bodeguita', 'inversiones', 'fragance', 'glow'];
                    if (skipWords.some(w => lower.includes(w))) continue;
                    
                    const categories = ['herramientas', 'belleza', 'deportes', 'hogar', 'salud'];
                    if (categories.includes(lower)) continue;
                    
                    name = line;
                    break;
                }
                
                if (!name || providerPrice === 0) continue;
                if (seen.has(uuid)) continue;
                seen.add(uuid);
                
                products.push({
                    uuid, name: name.substring(0, 60), providerPrice, profit, 
                    stock, sales7d, sales30d
                });
            }
            
            return products;
        }''')
    
    async def get_product_history(self, uuid: str, months: int = 6) -> Optional[Dict]:
        """Obtiene historial extendido (6 meses para cubrir 12+ semanas)"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            date_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            
            result = await self.page.evaluate('''async (params) => {
                const [uuid, dateRange] = params;
                try {
                    const response = await fetch(`/dashboard/tracking/detail/${uuid}?platform=dropi`, {
                        method: 'POST',
                        headers: {
                            'accept': 'text/x-component',
                            'content-type': 'text/plain;charset=UTF-8',
                            'next-action': '7ff80d9301fb1d1d96845742009470be0442d3283f'
                        },
                        body: JSON.stringify([uuid, dateRange])
                    });
                    const text = await response.text();
                    const lines = text.split('\\n');
                    for (const line of lines) {
                        if (line.startsWith('1:')) {
                            return JSON.parse(line.substring(2));
                        }
                    }
                    return null;
                } catch (e) {
                    return null;
                }
            }''', [uuid, date_range])
            
            return result
        except:
            return None
    
    async def get_products(self, country: str = "CO", min_sales: int = 10, 
                          max_products: int = 100, max_pages: int = 5) -> List[Dict]:
        print(f"  [2] Navegando a productos (ventas >= {min_sales})...")
        
        country_id = DROPKILLER_COUNTRIES.get(country, DROPKILLER_COUNTRIES["CO"])
        all_products = []
        seen_ids = set()
        
        try:
            for page_num in range(1, max_pages + 1):
                url = f"https://app.dropkiller.com/dashboard/products?country={country_id}&limit=50&page={page_num}&s7min={min_sales}"
                
                print(f"      Página {page_num}/{max_pages}...", end=" ", flush=True)
                await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await asyncio.sleep(4)
                
                for _ in range(3):
                    await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    await asyncio.sleep(0.5)
                
                page_products = await self.extract_products_with_uuid()
                
                new_count = 0
                for p in page_products:
                    pid = p.get('uuid', '')
                    if pid and pid not in seen_ids:
                        seen_ids.add(pid)
                        all_products.append(p)
                        new_count += 1
                
                print(f"→ {len(page_products)} extraídos, {new_count} nuevos | Total: {len(all_products)}")
                
                if new_count == 0 or len(all_products) >= max_products:
                    break
            
            all_products = [p for p in all_products if p.get('sales7d', 0) >= min_sales][:max_products]
            print(f"  [✓] Total: {len(all_products)} productos extraídos")
            
            return all_products
        except Exception as e:
            print(f"  [✗] Error: {e}")
            return all_products
    
    async def analyze_product_deep(self, product: Dict) -> Dict:
        uuid = product.get('uuid')
        if not uuid:
            return product
        
        # Obtener 6 meses de historial
        history_data = await self.get_product_history(uuid, months=6)
        
        if not history_data or 'data' not in history_data:
            product['trend'] = TrendAnalyzerV2._empty_analysis("No se pudo obtener historial")
            return product
        
        data = history_data['data']
        history = history_data.get('history', [])
        
        trend = TrendAnalyzerV2.analyze(history, data.get('createdAt'))
        
        product['trend'] = trend
        product['provider_name'] = data.get('provider', {}).get('name', 'N/A')
        product['category'] = data.get('baseCategory', {}).get('name', 'N/A')
        product['created_at'] = data.get('createdAt')
        
        # Calcular margen y aplicar filtros
        margin = calculate_margin(product.get('providerPrice', 35000))
        product['margin'] = margin
        product['filtro_result'] = FiltroExperto.aplicar_filtros(product, trend, margin)
        
        return product

    async def close(self):
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            await self.playwright.stop()


# ============== REPORT GENERATOR ==============
def print_filtro_stats(stats: Dict):
    """Imprime estadísticas de filtrado"""
    print("\n" + "=" * 75)
    print("  🎯 RESULTADO DE FILTROS EXPERTO v7.3")
    print("=" * 75)
    print(f"\n  📊 Analizados: {stats['total_analizados']} productos")
    print(f"  ✅ Pasaron filtros: {stats['pasaron']}")
    print(f"  ❌ Descartados: {stats['descartados']}")
    
    if stats['razones']:
        print(f"\n  📋 Razones de descarte:")
        for razon, count in sorted(stats['razones'].items(), key=lambda x: -x[1]):
            pct = (count / stats['descartados'] * 100) if stats['descartados'] > 0 else 0
            print(f"      • {razon}: {count} ({pct:.0f}%)")
    
    tasa = (stats['pasaron'] / stats['total_analizados'] * 100) if stats['total_analizados'] > 0 else 0
    print(f"\n  📈 Tasa de aprobación: {tasa:.1f}%")


def print_product_analysis(rank: int, product: Dict, show_details: bool = True):
    """Imprime análisis detallado de un producto aprobado"""
    name = product.get('name', 'N/A')[:40]
    trend = product.get('trend')
    margin = product.get('margin', calculate_margin(product.get('providerPrice', 35000)))
    filtro = product.get('filtro_result')
    
    if not trend:
        return
    
    score = trend.score
    stars = "⭐" * (score // 20) if score > 0 else "💀"
    
    pattern_emoji = {
        "DESPEGANDO": "🚀", "CRECIMIENTO_SOSTENIDO": "📈", "ESTABLE": "📊",
        "DECAYENDO": "📉", "VIRAL_MUERTO": "💀", "PICO_UNICO": "⚠️",
        "INCONSISTENTE": "🔴", "SIN_DATOS": "❓", "EVALUAR": "🔍",
        "APARICION_SUBITA": "🆕"
    }.get(trend.pattern, "❓")
    
    print(f"\n  #{rank}. {name}")
    print(f"      Score: {score}/100 {stars} | {pattern_emoji} {trend.pattern}")
    print(f"      Precio: ${product.get('providerPrice', 0):,} → ${margin['optimal_price']:,} | ROI: {margin['roi']}%")
    print(f"      📅 Historial: {trend.semanas_con_50_ventas}/12 semanas con ≥50 ventas")
    
    if show_details and trend.weeks:
        print(f"      ┌─────────────────────────────────────────────────")
        print(f"      │ VENTAS POR SEMANA (últimas 12):")
        for w in trend.weeks[:12]:
            week_label = "Actual" if w.week_number == 0 else f"Sem -{w.week_number}"
            bar_len = min(20, w.total_sales // 10) if w.total_sales > 0 else 0
            bar = "█" * bar_len if w.total_sales >= 50 else "░" * max(1, bar_len)
            check = "✓" if w.total_sales >= 50 else "✗"
            print(f"      │  {week_label:8} │ {w.total_sales:4} ventas │ {w.days_with_sales}/7 días │ {check} {bar}")
        
        if trend.week_over_week_growth:
            growth_str = " → ".join([f"{g:+.0f}%" for g in trend.week_over_week_growth[:3]])
            print(f"      │ Crecimiento: {growth_str}")
        
        print(f"      └─────────────────────────────────────────────────")
    
    # Métricas del filtro
    if filtro and filtro.metricas:
        m = filtro.metricas
        print(f"      ✅ V7d: {m.get('ventas_7d', 0)} | Días: {m.get('dias_activos', 0)}/7 | WoW: {m.get('caida_wow', 0):+.0f}% | ROI: {m.get('roi', 0):.0f}%")
    
    if trend.alerts:
        for alert in trend.alerts[:2]:
            print(f"      {alert}")
    
    print(f"      📋 {trend.pattern_reason}")


def print_descartados_resumen(productos: List[Dict], max_show: int = 10):
    """Muestra resumen de productos descartados"""
    descartados = [p for p in productos if p.get('filtro_result') and not p['filtro_result'].pasa]
    
    if not descartados:
        return
    
    print("\n" + "-" * 75)
    print(f"  ❌ DESCARTADOS ({len(descartados)} productos)")
    print("-" * 75)
    
    for p in descartados[:max_show]:
        name = p.get('name', 'N/A')[:30]
        filtro = p.get('filtro_result')
        trend = p.get('trend')
        semanas = trend.semanas_con_50_ventas if trend else 0
        razones = filtro.razones_descarte[0][:35] if filtro and filtro.razones_descarte else "Sin datos"
        print(f"      • {name}: [{semanas}/12 sem] → {razones}")
    
    if len(descartados) > max_show:
        print(f"      ... y {len(descartados) - max_show} más")


# ============== MAIN ==============
async def main():
    parser = argparse.ArgumentParser(description="DropKiller Scraper v7.3 - Filtros Experto (12 semanas)")
    parser.add_argument("--min-sales", type=int, default=10, help="Ventas mínimas 7d para extracción inicial")
    parser.add_argument("--max-products", type=int, default=100, help="Máx productos a extraer")
    parser.add_argument("--max-pages", type=int, default=5, help="Máx páginas")
    parser.add_argument("--country", default="CO", help="País")
    parser.add_argument("--visible", action="store_true", help="Mostrar navegador")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    parser.add_argument("--top", type=int, default=20, help="Mostrar top N productos aprobados")
    parser.add_argument("--show-descartados", action="store_true", help="Mostrar productos descartados")
    args = parser.parse_args()
    
    if not DROPKILLER_EMAIL or not DROPKILLER_PASSWORD:
        print("ERROR: Falta DROPKILLER_EMAIL o DROPKILLER_PASSWORD en .env")
        sys.exit(1)
    
    print("=" * 75)
    print("  ESTRATEGAS IA - Scraper v7.3 | Filtros Experto (12 semanas)")
    print("=" * 75)
    print(f"  País: {args.country} | Extracción: ventas >= {args.min_sales}")
    print(f"  Filtros: 12 sem ≥50v | V7d≥50 | Días≥4/7 | Caída≤30% | ROI≥20%")
    print("=" * 75)
    
    scraper = DropKillerScraper(DROPKILLER_EMAIL, DROPKILLER_PASSWORD, debug=args.debug)
    
    try:
        # FASE 1: Login
        print("\n[FASE 1] Login")
        await scraper.init_browser(headless=not args.visible)
        
        if not await scraper.login():
            print("\nERROR: Login fallido")
            return
        
        # FASE 2: Extracción
        print("\n[FASE 2] Extracción de productos")
        products = await scraper.get_products(args.country, args.min_sales, args.max_products, args.max_pages)
        
        if not products:
            print("\nNo se encontraron productos.")
            return
        
        # FASE 3: Análisis profundo + Filtros
        print(f"\n[FASE 3] Análisis profundo + Filtros ({len(products)} productos)...")
        print(f"         (Analizando 12 semanas de historial por producto)")
        
        for i, product in enumerate(products, 1):
            name = product.get('name', 'N/A')[:25]
            print(f"      [{i}/{len(products)}] {name}...", end=" ", flush=True)
            
            product = await scraper.analyze_product_deep(product)
            products[i-1] = product
            
            trend = product.get('trend')
            filtro = product.get('filtro_result')
            
            if filtro and filtro.pasa:
                print(f"✅ PASA | {trend.semanas_con_50_ventas}/12 sem | {trend.pattern[:10] if trend else '?'}")
            elif trend:
                sem = trend.semanas_con_50_ventas
                print(f"❌ {sem}/12 sem | {filtro.razones_descarte[0][:30] if filtro else '?'}")
            else:
                print("❌ Sin datos")
            
            await asyncio.sleep(0.3)
        
        # FASE 4: Resultados
        stats = FiltroExperto.resumen_filtros(products)
        print_filtro_stats(stats)
        
        # Productos aprobados
        aprobados = [p for p in products if p.get('filtro_result') and p['filtro_result'].pasa]
        
        if aprobados:
            # Ordenar por score
            aprobados.sort(key=lambda x: x.get('trend', TrendAnalysis(
                weeks=[], total_sold=0, total_days=0, week_over_week_growth=[],
                pattern="", pattern_reason="", alerts=[], score=0, peak_week=0, peak_vs_current=0,
                semanas_con_50_ventas=0, historial_solido=False
            )).score, reverse=True)
            
            print("\n" + "=" * 75)
            print(f"  🏆 PRODUCTOS APROBADOS ({len(aprobados)}) - HISTORIAL PROBADO 12+ SEMANAS")
            print("=" * 75)
            
            for rank, product in enumerate(aprobados[:args.top], 1):
                print_product_analysis(rank, product, show_details=True)
        else:
            print("\n" + "=" * 75)
            print("  ⚠️ NINGÚN PRODUCTO PASÓ LOS FILTROS")
            print("=" * 75)
            print("\n  Los filtros son MUY estrictos (12 semanas con ≥50 ventas).")
            print("  Esto es intencional - solo queremos productos PROBADOS.")
            print("\n  Considera:")
            print("      • Aumentar --max-products a 200-500")
            print("      • Revisar --show-descartados para ver qué tan cerca estuvieron")
        
        # Mostrar descartados si se pide
        if args.show_descartados:
            print_descartados_resumen(products, max_show=15)
        
        print("\n" + "=" * 75)
        print("  ✓ Análisis completado")
        print("=" * 75)
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
