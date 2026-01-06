#!/usr/bin/env python3
"""
Scraper Automático de DropKiller - Estrategas IA v6.2
NUEVO: Detección de picos únicos, virales muertos y manipulación de stock
Analiza consistencia de ventas diarias para identificar productos engañosos
"""

import os
import sys
import json
import re
import argparse
import asyncio
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
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

# Clasificación de tendencias
TREND_PATTERNS = {
    "DESPEGANDO": "🚀 Crecimiento explosivo Y consistente",
    "CRECIMIENTO_SOSTENIDO": "📈 Crecimiento constante por varios días",
    "ESTABLE": "📊 Ventas estables, mercado maduro",
    "DECAYENDO": "📉 Tendencia negativa clara",
    "VOLATIL": "🎢 Picos impredecibles",
    "NUEVO_SIN_DATOS": "🆕 Muy nuevo para evaluar",
    # NUEVOS - Detección de fraude/engaño
    "PICO_UNICO": "⚠️ Un solo día tiene >60% de ventas",
    "VIRAL_MUERTO": "💀 Tuvo un pico y murió",
    "INCONSISTENTE": "🔴 Muy pocos días con ventas reales",
    "SOSPECHOSO": "🚨 Posible manipulación de stock"
}

# Veredictos de mercado
MARKET_VERDICTS = {
    "OPORTUNIDAD_ALTA": "🎯 Poca o nula competencia",
    "OPORTUNIDAD_MEDIA": "✅ Mercado viable, competencia moderada",
    "SATURADO": "⚠️ Muchos competidores, difícil diferenciarse",
    "DECAYENDO": "❌ Mercado en declive, evitar",
    "DOMINADO": "🏆 Un competidor domina >50% del mercado"
}


# ============== DATA CLASSES ==============
@dataclass
class Competitor:
    """Competidor individual"""
    uuid: str
    provider_name: str
    sales_7d: int
    sales_30d: int
    price: int
    stock: int
    trend_pattern: str = ""
    trend_score: int = 0
    growth_7d: float = 0
    market_share: float = 0


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


# ============== TREND ANALYZER v2 ==============
class TrendAnalyzer:
    """Analiza histórico de ventas con detección de picos sospechosos"""
    
    @staticmethod
    def analyze_history(history: List[Dict], created_at: str = None) -> Dict:
        if not history:
            return {
                "trend_pattern": "NUEVO_SIN_DATOS",
                "trend_score": 0,
                "growth_rate_7d": 0,
                "growth_rate_30d": 0,
                "is_growing": False,
                "avg_daily": 0,
                "total_sold": 0,
                "consistency_score": 0,
                "is_suspicious": False,
                "days_with_sales": 0
            }
        
        sorted_history = sorted(history, key=lambda x: x.get('date', ''))
        
        # Extraer ventas diarias
        daily_sales = [d.get('soldUnits', 0) for d in sorted_history]
        total_sold = sum(daily_sales)
        
        if total_sold == 0:
            return {
                "trend_pattern": "NUEVO_SIN_DATOS",
                "trend_score": 0,
                "growth_rate_7d": 0,
                "growth_rate_30d": 0,
                "is_growing": False,
                "avg_daily": 0,
                "total_sold": 0,
                "consistency_score": 0,
                "is_suspicious": False,
                "days_with_sales": 0
            }
        
        # === ANÁLISIS DE CONSISTENCIA ===
        days_with_sales = len([s for s in daily_sales if s > 0])
        total_days = len(daily_sales)
        
        # Consistencia = % de días con ventas
        consistency_score = (days_with_sales / total_days * 100) if total_days > 0 else 0
        
        # Promedio y máximo
        avg_daily = total_sold / max(days_with_sales, 1)
        max_daily = max(daily_sales) if daily_sales else 0
        
        # === DETECCIÓN DE PICOS SOSPECHOSOS ===
        # Si el día máximo tiene >50% de las ventas totales = sospechoso
        max_day_ratio = (max_daily / total_sold * 100) if total_sold > 0 else 0
        
        # Top 3 días vs resto
        sorted_sales = sorted(daily_sales, reverse=True)
        top_3_sales = sum(sorted_sales[:3])
        top_3_ratio = (top_3_sales / total_sold * 100) if total_sold > 0 else 0
        
        # Detectar pico único (viral muerto o manipulación)
        is_suspicious = False
        suspicious_reason = ""
        
        if max_day_ratio > 50:
            is_suspicious = True
            suspicious_reason = f"Un solo día tiene {max_day_ratio:.0f}% de ventas"
        elif top_3_ratio > 80 and days_with_sales > 7:
            is_suspicious = True
            suspicious_reason = f"3 días tienen {top_3_ratio:.0f}% de ventas"
        elif consistency_score < 20 and total_days > 30:
            is_suspicious = True
            suspicious_reason = f"Solo {consistency_score:.0f}% de días con ventas"
        
        # === ANÁLISIS POR PERÍODOS ===
        last_7_days = sorted_history[-7:] if len(sorted_history) >= 7 else sorted_history
        last_30_days = sorted_history[-30:] if len(sorted_history) >= 30 else sorted_history
        prev_30_days = sorted_history[-60:-30] if len(sorted_history) >= 60 else []
        
        sales_7d = sum(d.get('soldUnits', 0) for d in last_7_days)
        sales_30d = sum(d.get('soldUnits', 0) for d in last_30_days)
        sales_prev_30d = sum(d.get('soldUnits', 0) for d in prev_30_days) if prev_30_days else 0
        
        # Días con ventas en últimos 7 y 30 días
        days_active_7d = len([d for d in last_7_days if d.get('soldUnits', 0) > 0])
        days_active_30d = len([d for d in last_30_days if d.get('soldUnits', 0) > 0])
        
        avg_30d = sales_30d / min(len(last_30_days), 30)
        expected_7d = avg_30d * 7
        growth_rate_7d = ((sales_7d - expected_7d) / expected_7d * 100) if expected_7d > 0 else 0
        growth_rate_30d = ((sales_30d - sales_prev_30d) / sales_prev_30d * 100) if sales_prev_30d > 0 else 100
        
        # === CLASIFICACIÓN FINAL ===
        trend_pattern, trend_score = TrendAnalyzer._classify_pattern(
            sales_7d=sales_7d,
            sales_30d=sales_30d,
            avg_7d=sales_7d/7,
            avg_30d=avg_30d,
            growth_7d=growth_rate_7d,
            growth_30d=growth_rate_30d,
            total_sold=total_sold,
            days_with_sales=days_with_sales,
            days_active_7d=days_active_7d,
            days_active_30d=days_active_30d,
            consistency_score=consistency_score,
            is_suspicious=is_suspicious,
            max_day_ratio=max_day_ratio,
            created_at=created_at
        )
        
        return {
            "trend_pattern": trend_pattern,
            "trend_score": trend_score,
            "growth_rate_7d": round(growth_rate_7d, 1),
            "growth_rate_30d": round(growth_rate_30d, 1),
            "is_growing": growth_rate_7d > 10 or growth_rate_30d > 20,
            "avg_daily": round(avg_daily, 1),
            "total_sold": total_sold,
            "consistency_score": round(consistency_score, 1),
            "is_suspicious": is_suspicious,
            "suspicious_reason": suspicious_reason,
            "days_with_sales": days_with_sales,
            "days_active_7d": days_active_7d,
            "days_active_30d": days_active_30d,
            "max_daily": max_daily,
            "max_day_ratio": round(max_day_ratio, 1)
        }
    
    @staticmethod
    def _classify_pattern(sales_7d, sales_30d, avg_7d, avg_30d, growth_7d, growth_30d, 
                          total_sold, days_with_sales, days_active_7d, days_active_30d,
                          consistency_score, is_suspicious, max_day_ratio, created_at) -> tuple:
        
        # Calcular edad
        age_days = days_with_sales
        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                age_days = (datetime.now(created.tzinfo) - created).days
            except:
                pass
        
        # === FILTROS DE SOSPECHA PRIMERO ===
        
        # PICO ÚNICO - Un día tiene >60% de todas las ventas
        if max_day_ratio > 60:
            return "PICO_UNICO", 15
        
        # VIRAL MUERTO - Tuvo un pico y murió
        if is_suspicious and days_active_7d <= 2 and sales_7d < sales_30d * 0.1:
            return "VIRAL_MUERTO", 10
        
        # INCONSISTENTE - Muy pocos días con ventas
        if consistency_score < 15 and days_with_sales > 7:
            return "INCONSISTENTE", 20
        
        # MANIPULACIÓN POSIBLE - Picos aleatorios sin patrón
        if is_suspicious and consistency_score < 30:
            return "SOSPECHOSO", 25
        
        # === PATRONES POSITIVOS ===
        
        # DESPEGANDO - Producto nuevo con crecimiento explosivo Y consistente
        if age_days < 90 and growth_7d > 50 and avg_7d > 10 and days_active_7d >= 5:
            return "DESPEGANDO", 95
        
        if age_days < 90 and growth_30d > 100 and avg_7d > 5 and days_active_7d >= 4:
            return "DESPEGANDO", 90
        
        # CRECIMIENTO SOSTENIDO - Consistente y creciendo
        if days_active_7d >= 5 and growth_7d > 20 and consistency_score > 40:
            return "CRECIMIENTO_SOSTENIDO", 85
        
        if age_days >= 60 and growth_30d > 30 and days_active_30d >= 15:
            return "CRECIMIENTO_SOSTENIDO", 80
        
        # ESTABLE - Ventas constantes
        if abs(growth_7d) < 25 and days_active_7d >= 4 and consistency_score > 35:
            if avg_7d > 20:
                return "ESTABLE", 75
            elif avg_7d > 5:
                return "ESTABLE", 65
        
        # === PATRONES NEGATIVOS ===
        
        # DECAYENDO - Claramente bajando
        if growth_7d < -40 and days_active_7d <= 3:
            return "DECAYENDO", 20
        
        if growth_30d < -50:
            return "DECAYENDO", 25
        
        # VOLÁTIL - Sube y baja sin patrón claro
        if abs(growth_7d) > 60 and consistency_score < 50:
            return "VOLATIL", 35
        
        # === CASOS EDGE ===
        
        # Muy nuevo para evaluar
        if days_with_sales < 10 or total_sold < 30:
            return "NUEVO_SIN_DATOS", 40
        
        # Default basado en tendencia reciente
        if days_active_7d >= 4 and growth_7d > 0:
            return "CRECIMIENTO_SOSTENIDO", 65
        elif days_active_7d >= 3 and abs(growth_7d) < 20:
            return "ESTABLE", 55
        elif growth_7d < -20:
            return "DECAYENDO", 35
        
        return "ESTABLE", 50


# ============== MARKET ANALYZER ==============
class MarketAnalyzer:
    """Analiza el mercado completo de un producto"""
    
    @staticmethod
    def analyze_market(competitors: List[Competitor], product_name: str) -> MarketAnalysis:
        """Analiza todos los competidores y genera veredicto de mercado"""
        
        if not competitors:
            return MarketAnalysis(
                product_name=product_name,
                search_term=product_name,
                verdict="NUEVO_SIN_DATOS",
                verdict_reason="No se encontraron competidores"
            )
        
        # Calcular totales
        total_sales_7d = sum(c.sales_7d for c in competitors)
        total_sales_30d = sum(c.sales_30d for c in competitors)
        
        # Calcular market share
        for comp in competitors:
            comp.market_share = (comp.sales_7d / total_sales_7d * 100) if total_sales_7d > 0 else 0
        
        # Ordenar por ventas
        competitors.sort(key=lambda x: x.sales_7d, reverse=True)
        
        # Calcular tendencia del mercado (promedio ponderado)
        if total_sales_30d > 0:
            market_growth = ((total_sales_7d * 4.28) - total_sales_30d) / total_sales_30d * 100
        else:
            market_growth = 0
        
        # Determinar tendencia general del mercado
        growing_count = sum(1 for c in competitors if c.growth_7d > 10)
        declining_count = sum(1 for c in competitors if c.growth_7d < -20)
        
        if growing_count > len(competitors) / 2:
            market_trend = "CRECIENDO"
        elif declining_count > len(competitors) / 2:
            market_trend = "DECAYENDO"
        else:
            market_trend = "ESTABLE"
        
        # Market share del líder
        leader_share = competitors[0].market_share if competitors else 0
        
        # Generar veredicto
        verdict, reason = MarketAnalyzer._generate_verdict(
            len(competitors), total_sales_7d, market_growth, 
            leader_share, market_trend
        )
        
        return MarketAnalysis(
            product_name=product_name,
            search_term=product_name,
            total_sales_7d=total_sales_7d,
            total_sales_30d=total_sales_30d,
            competitor_count=len(competitors),
            competitors=competitors,
            market_trend=market_trend,
            market_growth_7d=round(market_growth, 1),
            leader_share=round(leader_share, 1),
            verdict=verdict,
            verdict_reason=reason
        )
    
    @staticmethod
    def _generate_verdict(num_competitors: int, total_sales: int, growth: float, 
                          leader_share: float, trend: str) -> tuple:
        """Genera veredicto basado en métricas de mercado"""
        
        # Mercado en declive severo
        if growth < -40:
            return "DECAYENDO", f"Mercado cayendo {growth:.0f}%, evitar entrada"
        
        # 1-2 competidores = OPORTUNIDAD ALTA (no hay competencia real)
        if num_competitors <= 2:
            if growth > 0:
                return "OPORTUNIDAD_ALTA", f"Solo {num_competitors} proveedor(es), mercado creciendo {growth:.0f}%"
            elif growth > -20:
                return "OPORTUNIDAD_ALTA", f"Solo {num_competitors} proveedor(es), sin competencia real"
            else:
                return "OPORTUNIDAD_MEDIA", f"Solo {num_competitors} proveedor(es), mercado estable"
        
        # 3-4 competidores = Buena oportunidad
        if num_competitors <= 4:
            if growth > 10:
                return "OPORTUNIDAD_ALTA", f"{num_competitors} competidores, mercado creciendo {growth:.0f}%"
            elif growth > -15:
                return "OPORTUNIDAD_MEDIA", f"{num_competitors} competidores, mercado estable"
            else:
                return "DECAYENDO", f"Mercado cayendo {growth:.0f}% con {num_competitors} competidores"
        
        # 5-7 competidores = Competitivo
        if num_competitors <= 7:
            if leader_share > 50:
                return "DOMINADO", f"Líder tiene {leader_share:.0f}% con {num_competitors} competidores"
            elif growth > 0:
                return "OPORTUNIDAD_MEDIA", f"{num_competitors} competidores pero mercado creciendo"
            else:
                return "SATURADO", f"{num_competitors} competidores, mercado estancado"
        
        # 8+ competidores = Saturado
        if leader_share > 40:
            return "DOMINADO", f"Líder domina ({leader_share:.0f}%) entre {num_competitors} competidores"
        else:
            return "SATURADO", f"{num_competitors} competidores, mercado fragmentado"


# ============== DROPKILLER SCRAPER v6.2 ==============
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
                const providerUuid = uniqueUuids.length > 1 ? uniqueUuids[1] : null;
                
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
                    stock, sales7d, sales30d, providerUuid, externalId: uuid
                });
            }
            
            return products;
        }''')
    
    async def get_product_history(self, uuid: str, months: int = 6) -> Optional[Dict]:
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
        
        # Limpiar término de búsqueda - usar solo 2 palabras clave principales
        clean_term = search_term.lower().strip()
        # Filtrar palabras cortas y números
        keywords = [w for w in clean_term.split() if len(w) > 2 and not w.isdigit()][:2]
        search_query = "+".join(keywords) if keywords else clean_term.split()[0]
        
        url = f"https://app.dropkiller.com/dashboard/products?text={search_query}&country={country_id}&limit={limit}&page=1"
        
        if self.debug:
            print(f"        Buscando: {search_query}")
        
        await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)
        
        # Scroll para cargar todos
        for _ in range(2):
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(0.5)
        
        return await self.extract_products_with_uuid()
    
    async def get_products(self, country: str = "CO", min_sales: int = 20, 
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
    
    async def analyze_single_product(self, product: Dict) -> Dict:
        """Analiza histórico de un solo producto"""
        uuid = product.get('uuid')
        if not uuid:
            return product
        
        history_data = await self.get_product_history(uuid)
        
        if not history_data or 'data' not in history_data:
            product['trend_pattern'] = 'NUEVO_SIN_DATOS'
            product['trend_score'] = 40
            product['growth_rate_7d'] = 0
            product['is_growing'] = False
            product['consistency_score'] = 0
            product['days_active_7d'] = 0
            product['is_suspicious'] = False
            return product
        
        data = history_data['data']
        history = history_data.get('history', [])
        
        trend_result = TrendAnalyzer.analyze_history(history, data.get('createdAt'))
        
        product['created_at'] = data.get('createdAt')
        product['total_sold'] = data.get('totalSoldUnits', 0)
        product['trend_pattern'] = trend_result['trend_pattern']
        product['trend_score'] = trend_result['trend_score']
        product['growth_rate_7d'] = trend_result['growth_rate_7d']
        product['growth_rate_30d'] = trend_result['growth_rate_30d']
        product['is_growing'] = trend_result['is_growing']
        product['avg_daily'] = trend_result['avg_daily']
        product['provider_name'] = data.get('provider', {}).get('name', 'N/A')
        product['category'] = data.get('baseCategory', {}).get('name', 'N/A')
        
        # Nuevas métricas de consistencia
        product['consistency_score'] = trend_result.get('consistency_score', 0)
        product['days_with_sales'] = trend_result.get('days_with_sales', 0)
        product['days_active_7d'] = trend_result.get('days_active_7d', 0)
        product['days_active_30d'] = trend_result.get('days_active_30d', 0)
        product['is_suspicious'] = trend_result.get('is_suspicious', False)
        product['suspicious_reason'] = trend_result.get('suspicious_reason', '')
        product['max_daily'] = trend_result.get('max_daily', 0)
        product['max_day_ratio'] = trend_result.get('max_day_ratio', 0)
        
        return product
    
    async def analyze_market(self, product_name: str, country: str = "CO") -> MarketAnalysis:
        """Analiza el mercado completo de un producto"""
        
        # Buscar todos los competidores
        search_results = await self.search_products(product_name, country)
        
        if not search_results:
            return MarketAnalysis(
                product_name=product_name,
                search_term=product_name,
                verdict="NUEVO_SIN_DATOS",
                verdict_reason="No se encontraron productos similares"
            )
        
        # Analizar cada competidor
        competitors = []
        for prod in search_results[:10]:  # Máximo 10 competidores por producto
            analyzed = await self.analyze_single_product(prod)
            
            comp = Competitor(
                uuid=analyzed.get('uuid', ''),
                provider_name=analyzed.get('provider_name', 'N/A'),
                sales_7d=analyzed.get('sales7d', 0),
                sales_30d=analyzed.get('sales30d', 0),
                price=analyzed.get('providerPrice', 0),
                stock=analyzed.get('stock', 0),
                trend_pattern=analyzed.get('trend_pattern', ''),
                trend_score=analyzed.get('trend_score', 0),
                growth_7d=analyzed.get('growth_rate_7d', 0)
            )
            competitors.append(comp)
            
            await asyncio.sleep(0.3)  # Rate limiting
        
        # Generar análisis de mercado
        return MarketAnalyzer.analyze_market(competitors, product_name)

    async def close(self):
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            await self.playwright.stop()


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


# ============== MAIN ==============
async def main():
    parser = argparse.ArgumentParser(description="DropKiller Scraper v6.2 - Detección de Fraude")
    parser.add_argument("--min-sales", type=int, default=30, help="Ventas mínimas 7d")
    parser.add_argument("--max-products", type=int, default=50, help="Máx productos a extraer")
    parser.add_argument("--top-analyze", type=int, default=15, help="Top N productos para análisis de mercado")
    parser.add_argument("--max-pages", type=int, default=3, help="Máx páginas")
    parser.add_argument("--country", default="CO", help="País")
    parser.add_argument("--visible", action="store_true", help="Mostrar navegador")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    args = parser.parse_args()
    
    if not DROPKILLER_EMAIL or not DROPKILLER_PASSWORD:
        print("ERROR: Falta DROPKILLER_EMAIL o DROPKILLER_PASSWORD en .env")
        sys.exit(1)
    
    print("=" * 75)
    print("  ESTRATEGAS IA - Scraper v6.2 | Detección de Fraude + Análisis de Mercado")
    print("=" * 75)
    print(f"  País: {args.country} | Ventas mín: {args.min_sales}")
    print(f"  Máx productos: {args.max_products} | Análisis mercado: Top {args.top_analyze}")
    print("=" * 75)
    
    scraper = DropKillerScraper(DROPKILLER_EMAIL, DROPKILLER_PASSWORD, debug=args.debug)
    supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
    
    try:
        # FASE 1: Login
        print("\n[FASE 1] Login")
        await scraper.init_browser(headless=not args.visible)
        
        if not await scraper.login():
            print("\nERROR: Login fallido")
            return
        
        # FASE 2: Extracción inicial
        print("\n[FASE 2] Extracción de productos")
        products = await scraper.get_products(args.country, args.min_sales, args.max_products, args.max_pages)
        
        if not products:
            print("\nNo se encontraron productos.")
            return
        
        # FASE 3: Análisis de tendencia individual
        print(f"\n[FASE 3] Análisis de tendencia ({len(products)} productos)...")
        
        for i, product in enumerate(products, 1):
            name = product.get('name', 'N/A')[:25]
            print(f"      [{i}/{len(products)}] {name}...", end=" ", flush=True)
            
            product = await scraper.analyze_single_product(product)
            products[i-1] = product
            
            pattern = product.get('trend_pattern', 'N/A')
            consistency = product.get('consistency_score', 0)
            days_active = product.get('days_active_7d', 0)
            
            # Emojis según patrón
            emoji_map = {
                "DESPEGANDO": "🚀",
                "CRECIMIENTO_SOSTENIDO": "📈", 
                "ESTABLE": "📊",
                "DECAYENDO": "📉",
                "VOLATIL": "🎢",
                "NUEVO_SIN_DATOS": "🆕",
                "PICO_UNICO": "⚠️",
                "VIRAL_MUERTO": "💀",
                "INCONSISTENTE": "🔴",
                "SOSPECHOSO": "🚨"
            }
            emoji = emoji_map.get(pattern, "❓")
            
            # Mostrar info adicional para sospechosos
            if product.get('is_suspicious'):
                reason = product.get('suspicious_reason', '')[:30]
                print(f"{emoji} {pattern[:12]} | ⚠️ {reason}")
            else:
                print(f"{emoji} {pattern[:12]} | D7:{days_active}/7 C:{consistency:.0f}%")
            
            await asyncio.sleep(0.3)
        
        # Filtrar productos prometedores para análisis de mercado
        # NUEVO: Excluir sospechosos y requerir consistencia mínima
        suspicious_patterns = ["PICO_UNICO", "VIRAL_MUERTO", "INCONSISTENTE", "SOSPECHOSO"]
        
        promising = [
            p for p in products 
            if p.get('trend_score', 0) >= 60 
            and p.get('sales7d', 0) >= 50
            and p.get('trend_pattern') not in suspicious_patterns
            and p.get('days_active_7d', 0) >= 3  # Mínimo 3 días con ventas en última semana
        ]
        
        # También guardar los sospechosos para mostrar advertencia
        suspicious = [p for p in products if p.get('trend_pattern') in suspicious_patterns]
        
        promising.sort(key=lambda x: (x.get('trend_score', 0), x.get('sales7d', 0)), reverse=True)
        top_for_market = promising[:args.top_analyze]
        
        print(f"\n  [✓] {len(promising)} productos prometedores, analizando mercado de {len(top_for_market)}")
        
        if suspicious:
            print(f"  [⚠️] {len(suspicious)} productos SOSPECHOSOS descartados:")
            for p in suspicious[:5]:
                print(f"      - {p.get('name', 'N/A')[:30]} ({p.get('trend_pattern')})")
        
        # FASE 4: Análisis de mercado
        print(f"\n[FASE 4] Análisis de mercado ({len(top_for_market)} productos)")
        
        market_analyses = []
        
        for i, product in enumerate(top_for_market, 1):
            name = product.get('name', 'N/A')
            print(f"\n      [{i}/{len(top_for_market)}] Analizando mercado: {name[:40]}...")
            
            market = await scraper.analyze_market(name, args.country)
            market_analyses.append((product, market))
            
            # Mostrar resultado
            verdict_emoji = "🎯" if "ALTA" in market.verdict else "✅" if "MEDIA" in market.verdict else "⚠️" if "SATURADO" in market.verdict else "❌"
            print(f"          {verdict_emoji} {market.verdict}: {market.competitor_count} competidores, {market.total_sales_7d} ventas/7d")
            print(f"          Líder: {market.leader_share:.0f}% | Mercado: {market.market_trend} ({market.market_growth_7d:+.0f}%)")
            
            await asyncio.sleep(1)  # Rate limiting entre búsquedas
        
        # FASE 5: Resumen y guardado
        print("\n" + "=" * 75)
        print("  📊 RESUMEN DE ANÁLISIS DE MERCADO")
        print("=" * 75)
        
        # Clasificar por veredicto
        opportunities_high = [(p, m) for p, m in market_analyses if m.verdict == "OPORTUNIDAD_ALTA"]
        opportunities_med = [(p, m) for p, m in market_analyses if m.verdict == "OPORTUNIDAD_MEDIA"]
        saturated = [(p, m) for p, m in market_analyses if m.verdict in ["SATURADO", "DOMINADO"]]
        declining = [(p, m) for p, m in market_analyses if m.verdict == "DECAYENDO"]
        
        print(f"\n  🎯 Oportunidad Alta: {len(opportunities_high)}")
        print(f"  ✅ Oportunidad Media: {len(opportunities_med)}")
        print(f"  ⚠️ Saturado/Dominado: {len(saturated)}")
        print(f"  ❌ Decayendo: {len(declining)}")
        if suspicious:
            print(f"  🚨 Sospechosos descartados: {len(suspicious)}")
        
        # Mostrar mejores oportunidades
        if opportunities_high or opportunities_med:
            print("\n" + "=" * 75)
            print("  🏆 MEJORES OPORTUNIDADES")
            print("=" * 75)
            
            best = opportunities_high + opportunities_med
            for i, (prod, market) in enumerate(best[:10], 1):
                name = prod.get('name', 'N/A')[:35]
                margin = calculate_margin(prod.get('providerPrice', 35000))
                
                emoji = "🎯" if market.verdict == "OPORTUNIDAD_ALTA" else "✅"
                print(f"\n  {i}. {emoji} {name}")
                print(f"     Mercado: {market.total_sales_7d} v/7d | {market.competitor_count} competidores | Líder: {market.leader_share:.0f}%")
                print(f"     Tu potencial: V7d {prod.get('sales7d', 0)} | Growth {prod.get('growth_rate_7d', 0):+.0f}% | ROI {margin['roi']}%")
                print(f"     Consistencia: {prod.get('days_active_7d', 0)}/7 días activos | {prod.get('consistency_score', 0):.0f}% consistencia")
                print(f"     Razón: {market.verdict_reason}")
                
                # Mostrar competidores principales
                if market.competitors:
                    print(f"     Competidores:")
                    for j, comp in enumerate(market.competitors[:3], 1):
                        print(f"       {j}. {comp.provider_name[:20]} - {comp.sales_7d} v/7d ({comp.market_share:.0f}%)")
        
        # Guardar en Supabase
        if supabase:
            print("\n  Guardando en Supabase...")
            for prod, market in market_analyses:
                margin = calculate_margin(prod.get('providerPrice', 35000))
                
                data = {
                    "external_id": prod.get('uuid', ''),
                    "platform": "dropi",
                    "country_code": args.country,
                    "name": prod.get('name', '')[:60],
                    "cost_price": prod.get('providerPrice', 0),
                    "optimal_price": margin["optimal_price"],
                    "sales_7d": prod.get('sales7d', 0),
                    "sales_30d": prod.get('sales30d', 0),
                    "roi": margin['roi'],
                    "trend_pattern": prod.get('trend_pattern', ''),
                    "trend_score": prod.get('trend_score', 0),
                    "growth_rate_7d": prod.get('growth_rate_7d', 0),
                    "is_growing": prod.get('is_growing', False),
                    # Métricas de consistencia
                    "consistency_score": prod.get('consistency_score', 0),
                    "days_active_7d": prod.get('days_active_7d', 0),
                    "days_active_30d": prod.get('days_active_30d', 0),
                    "is_suspicious": prod.get('is_suspicious', False),
                    "suspicious_reason": prod.get('suspicious_reason', ''),
                    "max_day_ratio": prod.get('max_day_ratio', 0),
                    # Campos de mercado
                    "market_total_sales_7d": market.total_sales_7d,
                    "market_competitor_count": market.competitor_count,
                    "market_leader_share": market.leader_share,
                    "market_growth_7d": market.market_growth_7d,
                    "market_verdict": market.verdict,
                    "market_verdict_reason": market.verdict_reason,
                    "is_recommended": market.verdict in ["OPORTUNIDAD_ALTA", "OPORTUNIDAD_MEDIA"] and not prod.get('is_suspicious', False),
                    "analyzed_at": datetime.now().isoformat()
                }
                supabase.upsert("analyzed_products", data)
        
        print("\n" + "=" * 75)
        print("  ✓ Análisis completado")
        print("=" * 75)
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
