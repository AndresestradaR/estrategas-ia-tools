#!/usr/bin/env python3
"""
Scraper Automático de DropKiller - Estrategas IA v7.1
REDISEÑO COMPLETO: Análisis profundo por ventanas semanales
FIX: Detecta APARICION_SUBITA cuando no hay historial previo
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


# ============== DATA CLASSES ==============
@dataclass
class WeeklyMetrics:
    """Métricas de una semana específica"""
    week_number: int  # 0 = actual, 1 = anterior, etc.
    total_sales: int
    days_with_sales: int
    avg_daily: float
    max_daily: int
    min_daily: int
    consistency: float  # % días con ventas


@dataclass
class TrendAnalysis:
    """Análisis completo de tendencia"""
    # Métricas por semana
    weeks: List[WeeklyMetrics]
    
    # Totales
    total_sold: int
    total_days: int
    
    # Comparaciones
    week_over_week_growth: List[float]  # [sem0 vs sem1, sem1 vs sem2, ...]
    
    # Detección de patrones
    pattern: str
    pattern_reason: str
    
    # Alertas específicas
    alerts: List[str]
    
    # Score final (0-100)
    score: int
    
    # Datos para debug
    peak_week: int  # Qué semana tuvo el pico
    peak_vs_current: float  # Pico / Actual


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
    # Info básica
    uuid: str
    name: str
    provider_name: str
    category: str
    price: int
    stock: int
    
    # Ventas
    sales_7d: int
    sales_30d: int
    
    # Análisis de tendencia
    trend: TrendAnalysis
    
    # Análisis de mercado
    market: Optional[MarketAnalysis]
    
    # ROI
    roi: float
    optimal_price: int
    
    # Score final compuesto
    final_score: int
    
    # Resumen ejecutivo
    summary: str
    recommendation: str


# ============== TREND ANALYZER v2 - ANÁLISIS POR VENTANAS ==============
class TrendAnalyzerV2:
    """
    Analizador de tendencias basado en comparación de ventanas semanales.
    
    En lugar de métricas agregadas, compara:
    - Semana 0 (actual) vs Semana 1 vs Semana 2 vs Semana 3
    - Detecta patrones reales como "pico y muerte"
    """
    
    @staticmethod
    def analyze(history: List[Dict], created_at: str = None) -> TrendAnalysis:
        """Análisis completo por ventanas semanales"""
        
        if not history:
            return TrendAnalyzerV2._empty_analysis("Sin datos históricos")
        
        # Ordenar por fecha descendente (más reciente primero)
        sorted_history = sorted(history, key=lambda x: x.get('date', ''), reverse=True)
        
        # Extraer ventas diarias
        daily_sales = [d.get('soldUnits', 0) for d in sorted_history]
        
        if not daily_sales or sum(daily_sales) == 0:
            return TrendAnalyzerV2._empty_analysis("Sin ventas registradas")
        
        # ============== DIVIDIR EN SEMANAS ==============
        weeks = []
        for week_num in range(4):  # 4 semanas
            start_idx = week_num * 7
            end_idx = start_idx + 7
            week_sales = daily_sales[start_idx:end_idx] if start_idx < len(daily_sales) else []
            
            if week_sales:
                weeks.append(TrendAnalyzerV2._calculate_week_metrics(week_num, week_sales))
            else:
                weeks.append(WeeklyMetrics(
                    week_number=week_num,
                    total_sales=0,
                    days_with_sales=0,
                    avg_daily=0,
                    max_daily=0,
                    min_daily=0,
                    consistency=0
                ))
        
        # ============== CALCULAR CRECIMIENTO SEMANA A SEMANA ==============
        wow_growth = []
        for i in range(len(weeks) - 1):
            current = weeks[i].total_sales
            previous = weeks[i + 1].total_sales
            if previous > 0:
                growth = ((current - previous) / previous) * 100
            else:
                growth = 100 if current > 0 else 0
            wow_growth.append(round(growth, 1))
        
        # ============== DETECTAR PICO ==============
        week_totals = [w.total_sales for w in weeks]
        max_sales = max(week_totals) if week_totals else 0
        peak_week = week_totals.index(max_sales) if max_sales > 0 else 0
        current_sales = weeks[0].total_sales if weeks else 0
        peak_vs_current = (max_sales / current_sales) if current_sales > 0 else float('inf')
        
        # ============== ANÁLISIS DE PATRÓN ==============
        pattern, pattern_reason, alerts, score = TrendAnalyzerV2._detect_pattern(
            weeks, wow_growth, peak_week, peak_vs_current, daily_sales
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
            peak_vs_current=round(peak_vs_current, 2)
        )
    
    @staticmethod
    def _calculate_week_metrics(week_num: int, sales: List[int]) -> WeeklyMetrics:
        """Calcula métricas de una semana"""
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
                        daily_sales: List[int]) -> Tuple[str, str, List[str], int]:
        """
        Detecta el patrón real de ventas.
        Retorna: (patrón, razón, alertas, score)
        """
        alerts = []
        
        if not weeks or weeks[0].total_sales == 0:
            return "SIN_DATOS", "No hay ventas en la última semana", ["❌ Producto sin actividad reciente"], 0
        
        w0 = weeks[0]  # Semana actual
        w1 = weeks[1] if len(weeks) > 1 else None
        w2 = weeks[2] if len(weeks) > 2 else None
        w3 = weeks[3] if len(weeks) > 3 else None
        
        # ============== DETECTAR APARICIÓN SÚBITA ==============
        # Si semanas anteriores están en 0 o muy bajas, es sospechoso
        if w1 and w2:
            prev_weeks_sales = (w1.total_sales + w2.total_sales)
            if prev_weeks_sales <= 5 and w0.total_sales > 20:
                # Apareció de la nada
                alerts.append(f"🆕 Sin historial previo (Sem-1: {w1.total_sales}, Sem-2: {w2.total_sales})")
                alerts.append(f"⚠️ Producto muy nuevo o datos incompletos")
                return (
                    "APARICION_SUBITA",
                    f"Apareció esta semana sin historial previo ({w0.total_sales} ventas vs {prev_weeks_sales} en 2 sem anteriores)",
                    alerts,
                    45  # Score bajo porque no hay historial para validar
                )
        
        # ============== DETECTAR VIRAL MUERTO ==============
        # Si el pico NO fue esta semana Y actual es menos del 40% del pico
        if peak_week > 0 and peak_vs_current > 2.5:
            peak_sales = weeks[peak_week].total_sales
            alerts.append(f"🚨 Pico en semana -{peak_week} ({peak_sales} ventas)")
            alerts.append(f"🚨 Actual es {int(100/peak_vs_current)}% del pico")
            return (
                "VIRAL_MUERTO", 
                f"Tuvo pico hace {peak_week} semana(s), ahora está en {int(100/peak_vs_current)}% de ese nivel",
                alerts,
                max(10, 40 - (peak_week * 10))  # Entre 10-30 score
            )
        
        # ============== DETECTAR PICO ÚNICO EN UN DÍA ==============
        if daily_sales:
            max_day = max(daily_sales[:14])  # Últimos 14 días
            total_14d = sum(daily_sales[:14])
            if total_14d > 0:
                max_day_ratio = (max_day / total_14d) * 100
                if max_day_ratio > 50:
                    alerts.append(f"🚨 Un día tuvo {max_day_ratio:.0f}% de las ventas de 14 días")
                    return (
                        "PICO_UNICO",
                        f"Un solo día concentró {max_day_ratio:.0f}% de las ventas",
                        alerts,
                        25
                    )
        
        # ============== DETECTAR DESPEGANDO ==============
        # Crecimiento consistente semana a semana - REQUIERE historial
        if w1 and w2:
            # Verificar que hay historial real (no solo esta semana)
            has_history = w1.total_sales > 10 or w2.total_sales > 10
            
            if has_history and wow_growth[0] > 20 and (len(wow_growth) < 2 or wow_growth[1] > 0):
                # Creciendo vs semana anterior Y semana anterior no caía
                if w0.consistency >= 50:
                    alerts.append(f"✅ Crecimiento: +{wow_growth[0]:.0f}% vs semana anterior")
                    alerts.append(f"✅ Activo {w0.days_with_sales}/7 días")
                    
                    # Calcular score basado en crecimiento y consistencia
                    score = min(95, 70 + int(wow_growth[0] / 5) + int(w0.consistency / 10))
                    
                    return (
                        "DESPEGANDO",
                        f"Crecimiento +{wow_growth[0]:.0f}% sostenido, {w0.days_with_sales}/7 días activos",
                        alerts,
                        score
                    )
        
        # ============== DETECTAR CRECIMIENTO SOSTENIDO ==============
        if w1:
            # Verificar que hay historial real
            has_history = w1.total_sales > 10
            
            if has_history and wow_growth[0] > 10 and w0.consistency >= 40:
                alerts.append(f"✅ Creciendo: +{wow_growth[0]:.0f}%")
                score = min(85, 60 + int(wow_growth[0] / 3))
                return (
                    "CRECIMIENTO_SOSTENIDO",
                    f"Crecimiento +{wow_growth[0]:.0f}%, buena consistencia",
                    alerts,
                    score
                )
        
        # ============== DETECTAR ESTABLE ==============
        if w1:
            if abs(wow_growth[0]) <= 20 and w0.consistency >= 40:
                alerts.append(f"📊 Variación: {wow_growth[0]:+.0f}%")
                alerts.append(f"📊 Consistencia: {w0.consistency:.0f}%")
                score = 55 + int(w0.consistency / 5)
                return (
                    "ESTABLE",
                    f"Ventas estables ({wow_growth[0]:+.0f}%), consistencia {w0.consistency:.0f}%",
                    alerts,
                    score
                )
        
        # ============== DETECTAR DECAYENDO ==============
        if w1:
            if wow_growth[0] < -20:
                alerts.append(f"📉 Cayendo: {wow_growth[0]:.0f}%")
                score = max(20, 50 + int(wow_growth[0] / 2))
                return (
                    "DECAYENDO",
                    f"Caída de {abs(wow_growth[0]):.0f}% vs semana anterior",
                    alerts,
                    score
                )
        
        # ============== DETECTAR INCONSISTENTE ==============
        if w0.consistency < 30:
            alerts.append(f"⚠️ Solo {w0.days_with_sales}/7 días con ventas")
            return (
                "INCONSISTENTE",
                f"Solo vende {w0.days_with_sales} días de 7",
                alerts,
                35
            )
        
        # ============== DEFAULT: EVALUAR ==============
        score = 50 + int(w0.consistency / 4)
        return (
            "EVALUAR",
            "Patrón no claro, requiere análisis manual",
            alerts,
            score
        )
    
    @staticmethod
    def _empty_analysis(reason: str) -> TrendAnalysis:
        """Retorna análisis vacío"""
        return TrendAnalysis(
            weeks=[],
            total_sold=0,
            total_days=0,
            week_over_week_growth=[],
            pattern="SIN_DATOS",
            pattern_reason=reason,
            alerts=["❌ " + reason],
            score=0,
            peak_week=0,
            peak_vs_current=0
        )


# ============== MARKET ANALYZER ==============
class MarketAnalyzer:
    """Analiza el mercado completo de un producto"""
    
    @staticmethod
    def analyze_market(competitors: List[Competitor], product_name: str) -> MarketAnalysis:
        if not competitors:
            return MarketAnalysis(
                product_name=product_name,
                search_term=product_name,
                verdict="SIN_DATOS",
                verdict_reason="No se encontraron competidores"
            )
        
        # Filtrar competidores con ventas
        active_competitors = [c for c in competitors if c.sales_7d > 0]
        
        total_sales_7d = sum(c.sales_7d for c in competitors)
        total_sales_30d = sum(c.sales_30d for c in competitors)
        
        # Calcular market share
        for comp in competitors:
            comp.market_share = (comp.sales_7d / total_sales_7d * 100) if total_sales_7d > 0 else 0
        
        competitors.sort(key=lambda x: x.sales_7d, reverse=True)
        
        # Calcular tendencia del mercado
        if total_sales_30d > 0:
            market_growth = ((total_sales_7d * 4.28) - total_sales_30d) / total_sales_30d * 100
        else:
            market_growth = 0
        
        # Determinar tendencia
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
            product_name=product_name,
            search_term=product_name,
            total_sales_7d=total_sales_7d,
            total_sales_30d=total_sales_30d,
            competitor_count=len(active_competitors),
            competitors=competitors,
            market_trend=market_trend,
            market_growth_7d=round(market_growth, 1),
            leader_share=round(leader_share, 1),
            verdict=verdict,
            verdict_reason=reason
        )
    
    @staticmethod
    def _generate_verdict(num_competitors: int, total_sales: int, growth: float, 
                          leader_share: float) -> Tuple[str, str]:
        
        if growth < -40:
            return "DECAYENDO", f"Mercado cayendo {growth:.0f}%"
        
        if num_competitors <= 2:
            if growth > 0:
                return "OPORTUNIDAD_ALTA", f"Solo {num_competitors} competidor(es), creciendo {growth:.0f}%"
            else:
                return "OPORTUNIDAD_ALTA", f"Solo {num_competitors} competidor(es), sin competencia real"
        
        if num_competitors <= 4:
            if growth > 10:
                return "OPORTUNIDAD_ALTA", f"{num_competitors} competidores, mercado creciendo {growth:.0f}%"
            elif growth > -15:
                return "OPORTUNIDAD_MEDIA", f"{num_competitors} competidores, mercado estable"
            else:
                return "DECAYENDO", f"Mercado cayendo {growth:.0f}%"
        
        if num_competitors <= 7:
            if leader_share > 50:
                return "DOMINADO", f"Líder tiene {leader_share:.0f}%"
            elif growth > 0:
                return "OPORTUNIDAD_MEDIA", f"{num_competitors} competidores, creciendo"
            else:
                return "SATURADO", f"{num_competitors} competidores"
        
        if leader_share > 40:
            return "DOMINADO", f"Líder domina ({leader_share:.0f}%)"
        else:
            return "SATURADO", f"{num_competitors}+ competidores"


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


# ============== DROPKILLER SCRAPER v7.1 ==============
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
        """Extrae productos incluyendo el UUID"""
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
    
    async def get_product_history(self, uuid: str, months: int = 3) -> Optional[Dict]:
        """Obtiene el histórico de un producto"""
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
    
    async def search_products(self, search_term: str, country: str = "CO", limit: int = 50) -> List[Dict]:
        """Busca productos por nombre"""
        country_id = DROPKILLER_COUNTRIES.get(country, DROPKILLER_COUNTRIES["CO"])
        
        clean_term = search_term.lower().strip()
        keywords = [w for w in clean_term.split() if len(w) > 2 and not w.isdigit()][:2]
        search_query = "+".join(keywords) if keywords else clean_term.split()[0]
        
        url = f"https://app.dropkiller.com/dashboard/products?text={search_query}&country={country_id}&limit={limit}&page=1"
        
        if self.debug:
            print(f"          🔍 Buscando: '{search_query}'")
        
        await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(4)
        
        for _ in range(3):
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)
        
        await asyncio.sleep(2)
        
        products = await self.extract_products_with_uuid()
        
        if self.debug:
            print(f"          📦 Encontrados: {len(products)} productos")
        
        return products
    
    async def get_products(self, country: str = "CO", min_sales: int = 10, 
                          max_products: int = 100, max_pages: int = 5) -> List[Dict]:
        """Extrae productos de DropKiller"""
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
        """Análisis profundo de un producto individual"""
        uuid = product.get('uuid')
        if not uuid:
            return product
        
        history_data = await self.get_product_history(uuid)
        
        if not history_data or 'data' not in history_data:
            product['trend'] = TrendAnalyzerV2._empty_analysis("No se pudo obtener historial")
            return product
        
        data = history_data['data']
        history = history_data.get('history', [])
        
        # Análisis profundo con v2
        trend = TrendAnalyzerV2.analyze(history, data.get('createdAt'))
        
        product['trend'] = trend
        product['provider_name'] = data.get('provider', {}).get('name', 'N/A')
        product['category'] = data.get('baseCategory', {}).get('name', 'N/A')
        product['created_at'] = data.get('createdAt')
        
        return product

    async def close(self):
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            await self.playwright.stop()


# ============== REPORT GENERATOR ==============
def print_product_analysis(rank: int, product: Dict, show_details: bool = True):
    """Imprime análisis detallado de un producto"""
    name = product.get('name', 'N/A')[:40]
    trend = product.get('trend')
    margin = calculate_margin(product.get('providerPrice', 35000))
    
    if not trend:
        print(f"\n  #{rank}. {name}")
        print(f"      ❌ Sin datos de análisis")
        return
    
    # Header con score
    score = trend.score
    stars = "⭐" * (score // 20) if score > 0 else "💀"
    
    pattern_emoji = {
        "DESPEGANDO": "🚀",
        "CRECIMIENTO_SOSTENIDO": "📈",
        "ESTABLE": "📊",
        "DECAYENDO": "📉",
        "VIRAL_MUERTO": "💀",
        "PICO_UNICO": "⚠️",
        "INCONSISTENTE": "🔴",
        "SIN_DATOS": "❓",
        "EVALUAR": "🔍",
        "APARICION_SUBITA": "🆕"
    }.get(trend.pattern, "❓")
    
    print(f"\n  #{rank}. {name}")
    print(f"      Score: {score}/100 {stars} | {pattern_emoji} {trend.pattern}")
    print(f"      Precio: ${product.get('providerPrice', 0):,} → ${margin['optimal_price']:,} | ROI: {margin['roi']}%")
    
    if show_details and trend.weeks:
        # Mostrar ventas por semana
        print(f"      ┌─────────────────────────────────────────────────")
        print(f"      │ VENTAS POR SEMANA:")
        for w in trend.weeks[:4]:
            week_label = "Actual" if w.week_number == 0 else f"Sem -{w.week_number}"
            bar = "█" * min(20, w.total_sales // 10) if w.total_sales > 0 else "░"
            print(f"      │  {week_label:8} │ {w.total_sales:4} ventas │ {w.days_with_sales}/7 días │ {bar}")
        
        # Mostrar crecimiento
        if trend.week_over_week_growth:
            growth_str = " → ".join([f"{g:+.0f}%" for g in trend.week_over_week_growth[:3]])
            print(f"      │ Crecimiento: {growth_str}")
        
        print(f"      └─────────────────────────────────────────────────")
    
    # Alertas
    if trend.alerts:
        for alert in trend.alerts[:3]:
            print(f"      {alert}")
    
    # Razón del patrón
    print(f"      📋 {trend.pattern_reason}")


def print_ranking_summary(products: List[Dict]):
    """Imprime resumen del ranking"""
    print("\n" + "=" * 75)
    print("  📊 RESUMEN DEL RANKING")
    print("=" * 75)
    
    patterns = defaultdict(list)
    for p in products:
        trend = p.get('trend')
        if trend:
            patterns[trend.pattern].append(p.get('name', 'N/A')[:25])
    
    pattern_order = ["DESPEGANDO", "CRECIMIENTO_SOSTENIDO", "ESTABLE", "EVALUAR", 
                     "APARICION_SUBITA", "DECAYENDO", "INCONSISTENTE", "PICO_UNICO", 
                     "VIRAL_MUERTO", "SIN_DATOS"]
    
    for pattern in pattern_order:
        if pattern in patterns:
            emoji = {
                "DESPEGANDO": "🚀",
                "CRECIMIENTO_SOSTENIDO": "📈",
                "ESTABLE": "📊",
                "DECAYENDO": "📉",
                "VIRAL_MUERTO": "💀",
                "PICO_UNICO": "⚠️",
                "INCONSISTENTE": "🔴",
                "SIN_DATOS": "❓",
                "EVALUAR": "🔍",
                "APARICION_SUBITA": "🆕"
            }.get(pattern, "❓")
            
            print(f"\n  {emoji} {pattern}: {len(patterns[pattern])} productos")
            for name in patterns[pattern][:5]:
                print(f"      - {name}")
            if len(patterns[pattern]) > 5:
                print(f"      ... y {len(patterns[pattern]) - 5} más")


# ============== MAIN ==============
async def main():
    parser = argparse.ArgumentParser(description="DropKiller Scraper v7.1 - Análisis Profundo")
    parser.add_argument("--min-sales", type=int, default=10, help="Ventas mínimas 7d")
    parser.add_argument("--max-products", type=int, default=50, help="Máx productos a extraer")
    parser.add_argument("--max-pages", type=int, default=3, help="Máx páginas")
    parser.add_argument("--country", default="CO", help="País")
    parser.add_argument("--visible", action="store_true", help="Mostrar navegador")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    parser.add_argument("--top", type=int, default=20, help="Mostrar top N productos")
    args = parser.parse_args()
    
    if not DROPKILLER_EMAIL or not DROPKILLER_PASSWORD:
        print("ERROR: Falta DROPKILLER_EMAIL o DROPKILLER_PASSWORD en .env")
        sys.exit(1)
    
    print("=" * 75)
    print("  ESTRATEGAS IA - Scraper v7.1 | Análisis Profundo por Ventanas")
    print("=" * 75)
    print(f"  País: {args.country} | Ventas mín: {args.min_sales}")
    print(f"  Máx productos: {args.max_products} | Mostrar top: {args.top}")
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
        
        # FASE 3: Análisis profundo
        print(f"\n[FASE 3] Análisis profundo ({len(products)} productos)...")
        
        for i, product in enumerate(products, 1):
            name = product.get('name', 'N/A')[:25]
            print(f"      [{i}/{len(products)}] {name}...", end=" ", flush=True)
            
            product = await scraper.analyze_product_deep(product)
            products[i-1] = product
            
            trend = product.get('trend')
            if trend:
                emoji = {
                    "DESPEGANDO": "🚀",
                    "CRECIMIENTO_SOSTENIDO": "📈",
                    "ESTABLE": "📊",
                    "DECAYENDO": "📉",
                    "VIRAL_MUERTO": "💀",
                    "PICO_UNICO": "⚠️",
                    "INCONSISTENTE": "🔴",
                    "SIN_DATOS": "❓",
                    "EVALUAR": "🔍",
                    "APARICION_SUBITA": "🆕"
                }.get(trend.pattern, "❓")
                print(f"{emoji} {trend.pattern[:15]} | Score: {trend.score}")
            else:
                print("❓ Sin datos")
            
            await asyncio.sleep(0.3)
        
        # FASE 4: Ranking
        print("\n" + "=" * 75)
        print("  🏆 RANKING DE PRODUCTOS (por Score)")
        print("=" * 75)
        
        # Ordenar por score
        products.sort(key=lambda x: x.get('trend', TrendAnalysis(
            weeks=[], total_sold=0, total_days=0, week_over_week_growth=[],
            pattern="", pattern_reason="", alerts=[], score=0, peak_week=0, peak_vs_current=0
        )).score, reverse=True)
        
        # Mostrar top N
        for rank, product in enumerate(products[:args.top], 1):
            print_product_analysis(rank, product, show_details=True)
        
        # Resumen
        print_ranking_summary(products)
        
        print("\n" + "=" * 75)
        print("  ✓ Análisis completado")
        print("=" * 75)
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
