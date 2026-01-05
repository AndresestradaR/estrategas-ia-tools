#!/usr/bin/env python3
"""
Scraper Automático de DropKiller - Estrategas IA v5.0
NUEVO: Extracción de UUID + API histórico 6 meses + Análisis de tendencia real
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
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# ============== CONFIG ==============
DROPKILLER_EMAIL = os.getenv("DROPKILLER_EMAIL", "")
DROPKILLER_PASSWORD = os.getenv("DROPKILLER_PASSWORD", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

DROPKILLER_COUNTRIES = {
    "CO": "65c75a5f-0c4a-45fb-8c90-5b538805a15a",
    "MX": "98993bd0-955a-4fa3-9612-c9d4389c44d0", 
    "EC": "82811e8b-d17d-4ab9-847a-fa925785d566",
}

# Clasificación de tendencias
TREND_PATTERNS = {
    "DESPEGANDO": "🚀 Producto nuevo con crecimiento explosivo",
    "CRECIMIENTO_SOSTENIDO": "📈 Crecimiento constante por varios meses",
    "ESTABLE": "📊 Ventas estables, mercado maduro",
    "DECAYENDO": "📉 Pasó su mejor momento",
    "VOLATIL": "🎢 Picos impredecibles",
    "NUEVO_SIN_DATOS": "🆕 Muy nuevo para evaluar tendencia"
}


# ============== DATA CLASSES ==============
@dataclass
class ProductHistory:
    """Histórico de un producto"""
    uuid: str
    name: str
    created_at: Optional[str]
    total_sold: int
    avg_daily: float
    history: List[Dict]
    trend_pattern: str
    trend_score: float
    growth_rate_7d: float
    growth_rate_30d: float
    is_growing: bool
    

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


# ============== TREND ANALYZER ==============
class TrendAnalyzer:
    """Analiza histórico de ventas para determinar tendencia"""
    
    @staticmethod
    def analyze_history(history: List[Dict], created_at: str = None) -> Dict:
        """
        Analiza el histórico y determina el patrón de tendencia
        
        history: Lista de {"date": "YYYY-MM-DD", "soldUnits": N, "stock": N, ...}
        """
        if not history:
            return {
                "trend_pattern": "NUEVO_SIN_DATOS",
                "trend_score": 0,
                "growth_rate_7d": 0,
                "growth_rate_30d": 0,
                "is_growing": False,
                "avg_daily": 0,
                "total_sold": 0
            }
        
        # Filtrar días con ventas válidas (soldUnits > 0 o tiene externalProductId)
        valid_days = [d for d in history if d.get('soldUnits', 0) > 0 or d.get('externalProductId')]
        
        if len(valid_days) < 7:
            return {
                "trend_pattern": "NUEVO_SIN_DATOS",
                "trend_score": 0,
                "growth_rate_7d": 0,
                "growth_rate_30d": 0,
                "is_growing": False,
                "avg_daily": 0,
                "total_sold": sum(d.get('soldUnits', 0) for d in history)
            }
        
        # Ordenar por fecha
        sorted_history = sorted(history, key=lambda x: x.get('date', ''))
        
        # Calcular ventas totales y promedio
        total_sold = sum(d.get('soldUnits', 0) for d in sorted_history)
        days_active = len([d for d in sorted_history if d.get('soldUnits', 0) > 0])
        avg_daily = total_sold / max(days_active, 1)
        
        # Dividir en períodos
        last_7_days = sorted_history[-7:] if len(sorted_history) >= 7 else sorted_history
        last_30_days = sorted_history[-30:] if len(sorted_history) >= 30 else sorted_history
        prev_30_days = sorted_history[-60:-30] if len(sorted_history) >= 60 else []
        first_30_days = sorted_history[:30] if len(sorted_history) >= 30 else sorted_history
        
        # Calcular ventas por período
        sales_7d = sum(d.get('soldUnits', 0) for d in last_7_days)
        sales_30d = sum(d.get('soldUnits', 0) for d in last_30_days)
        sales_prev_30d = sum(d.get('soldUnits', 0) for d in prev_30_days) if prev_30_days else 0
        sales_first_30d = sum(d.get('soldUnits', 0) for d in first_30_days)
        
        # Calcular promedios por período
        avg_7d = sales_7d / 7
        avg_30d = sales_30d / min(len(last_30_days), 30)
        avg_prev_30d = sales_prev_30d / 30 if prev_30_days else 0
        
        # Calcular ratios de crecimiento
        # Ratio 7d vs promedio 30d (ajustado a semana)
        expected_7d = avg_30d * 7
        growth_rate_7d = ((sales_7d - expected_7d) / expected_7d * 100) if expected_7d > 0 else 0
        
        # Ratio 30d vs 30d anterior
        growth_rate_30d = ((sales_30d - sales_prev_30d) / sales_prev_30d * 100) if sales_prev_30d > 0 else 100
        
        # Determinar patrón de tendencia
        trend_pattern, trend_score = TrendAnalyzer._classify_pattern(
            avg_7d, avg_30d, avg_prev_30d,
            growth_rate_7d, growth_rate_30d,
            total_sold, days_active, created_at
        )
        
        return {
            "trend_pattern": trend_pattern,
            "trend_score": trend_score,
            "growth_rate_7d": round(growth_rate_7d, 1),
            "growth_rate_30d": round(growth_rate_30d, 1),
            "is_growing": growth_rate_7d > 10 or growth_rate_30d > 20,
            "avg_daily": round(avg_daily, 1),
            "total_sold": total_sold,
            "sales_7d": sales_7d,
            "sales_30d": sales_30d,
            "sales_prev_30d": sales_prev_30d
        }
    
    @staticmethod
    def _classify_pattern(avg_7d, avg_30d, avg_prev_30d, growth_7d, growth_30d, total_sold, days_active, created_at) -> tuple:
        """Clasifica el patrón de tendencia"""
        
        # Calcular edad del producto
        age_days = days_active
        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                age_days = (datetime.now(created.tzinfo) - created).days
            except:
                pass
        
        # 1. DESPEGANDO - Producto nuevo (<90 días) con crecimiento explosivo
        if age_days < 90 and growth_7d > 50 and avg_7d > 10:
            return "DESPEGANDO", 95
        
        if age_days < 90 and growth_30d > 100 and avg_7d > 5:
            return "DESPEGANDO", 90
        
        # 2. CRECIMIENTO SOSTENIDO - Más de 90 días y sigue creciendo
        if age_days >= 90 and growth_30d > 30 and growth_7d > 0:
            return "CRECIMIENTO_SOSTENIDO", 85
        
        if age_days >= 60 and growth_30d > 50 and avg_7d > 20:
            return "CRECIMIENTO_SOSTENIDO", 80
        
        # 3. ESTABLE - Ventas constantes sin mucha variación
        if abs(growth_7d) < 20 and abs(growth_30d) < 30 and avg_7d > 5:
            if avg_7d > 30:
                return "ESTABLE", 70  # Estable con buen volumen
            return "ESTABLE", 60
        
        # 4. DECAYENDO - Tendencia negativa
        if growth_7d < -30 and growth_30d < -20:
            return "DECAYENDO", 20
        
        if growth_30d < -40:
            return "DECAYENDO", 25
        
        # 5. VOLATIL - Cambios bruscos sin patrón claro
        if abs(growth_7d) > 50 and abs(growth_30d) > 50:
            # Alta volatilidad pero con volumen
            if avg_7d > 20:
                return "VOLATIL", 50
            return "VOLATIL", 35
        
        # 6. NUEVO SIN DATOS - Muy pocos datos para evaluar
        if days_active < 14 or total_sold < 20:
            return "NUEVO_SIN_DATOS", 40
        
        # Default: Basado en si crece o no
        if growth_7d > 0:
            return "CRECIMIENTO_SOSTENIDO", 65
        elif growth_7d < -10:
            return "DECAYENDO", 35
        else:
            return "ESTABLE", 55


# ============== DROPKILLER SCRAPER v5 ==============
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
                
                # Guardar cookies de sesión
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
        """Extrae productos incluyendo el UUID del enlace Ver detalle"""
        return await self.page.evaluate('''() => {
            const products = [];
            const seen = new Set();
            
            // Buscar todos los enlaces "Ver detalle"
            const links = document.querySelectorAll('a[href*="/dashboard/tracking/detail/"]');
            
            for (const link of links) {
                // Extraer UUID del href
                const href = link.getAttribute('href') || '';
                const uuidMatch = href.match(/detail\\/([a-f0-9-]{36})/);
                if (!uuidMatch) continue;
                
                const uuid = uuidMatch[1];
                
                // Buscar la fila del producto
                let row = link.parentElement;
                for (let i = 0; i < 10 && row; i++) {
                    const text = row.innerText || '';
                    if (text.includes('Stock:') && text.includes('COP') && text.includes('Ver detalle')) {
                        break;
                    }
                    row = row.parentElement;
                }
                
                if (!row) continue;
                
                const text = row.innerText || '';
                const lines = text.split('\\n').map(l => l.trim()).filter(l => l);
                
                // Extraer Stock
                const stockMatch = text.match(/Stock:\\s*([\\d.,]+)/i);
                const stock = stockMatch ? parseInt(stockMatch[1].replace(/[.,]/g, '')) : 0;
                
                // Encontrar índices de líneas con COP
                const copIndices = [];
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i].includes('COP')) {
                        copIndices.push(i);
                    }
                }
                
                if (copIndices.length < 4) continue;
                
                const extractPrice = (line) => {
                    const match = line.match(/([\\d.]+)\\s*COP/);
                    if (match) {
                        return parseInt(match[1].replace(/\\./g, ''));
                    }
                    return 0;
                };
                
                const providerPrice = extractPrice(lines[copIndices[0]]);
                const profit = extractPrice(lines[copIndices[1]]);
                
                // Ventas 7d y 30d
                let sales7d = 0;
                let sales30d = 0;
                
                const salesStartIndex = copIndices[1] + 1;
                const salesEndIndex = copIndices[2];
                
                const salesLines = [];
                for (let i = salesStartIndex; i < salesEndIndex; i++) {
                    const line = lines[i];
                    const cleaned = line.replace(/\\./g, '');
                    if (/^\\d+$/.test(cleaned)) {
                        salesLines.push(parseInt(cleaned));
                    }
                }
                
                if (salesLines.length >= 1) sales7d = salesLines[0];
                if (salesLines.length >= 2) sales30d = salesLines[1];
                
                // Buscar nombre del producto
                let name = '';
                for (const line of lines) {
                    if (/^\\d{1,2}[\\/-]\\d{1,2}[\\/-]\\d{2,4}$/.test(line)) continue;
                    if (/^[\\d.,\\s]+$/.test(line)) continue;
                    if (/COP/.test(line)) continue;
                    if (line.startsWith('Stock:') || line.startsWith('Proveedor:') || line === 'Proveedor:') continue;
                    if (line.includes('Ver detalle') || line === 'ID') continue;
                    if (/^(Ventas|Facturación|Fecha|Página|Mostrar)/i.test(line)) continue;
                    if (line.length < 5 || line.length > 80) continue;
                    
                    const lower = line.toLowerCase();
                    const providerWords = ['shop', 'store', 'tienda', 'import', 'mayor', 
                                           'group', 'china', 'bodeguita', 'inversiones',
                                           'fragance', 'glow', 'perfumeria', 'goldbox',
                                           'vitalcom', 'worldsport', 'homie', 'tulastore',
                                           'diversidades', 'agrostock', 'krombi', 'fajas',
                                           'stockeado', 'prendas control', 'dads jackets',
                                           'toons mayorista', 'oh homie'];
                    if (providerWords.some(w => lower.includes(w))) continue;
                    
                    const categories = ['herramientas', 'belleza', 'deportes', 'hogar', 'salud', 
                                       'tecnologia', 'moda', 'mascotas', 'bebes', 'cocina'];
                    if (categories.includes(lower)) continue;
                    
                    name = line;
                    break;
                }
                
                if (!name || providerPrice === 0) continue;
                
                // Usar UUID como identificador único
                if (seen.has(uuid)) continue;
                seen.add(uuid);
                
                products.push({
                    uuid: uuid,
                    name: name.substring(0, 60),
                    providerPrice,
                    profit,
                    stock,
                    sales7d,
                    sales30d,
                    externalId: uuid
                });
            }
            
            return products;
        }''')
    
    async def get_product_history(self, uuid: str, months: int = 6) -> Optional[Dict]:
        """
        Obtiene el histórico de un producto usando la API de DropKiller
        
        uuid: UUID del producto
        months: Cantidad de meses de histórico (default 6)
        """
        try:
            # Calcular rango de fechas
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            date_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            
            # Preparar el request body
            body = json.dumps([uuid, date_range])
            
            # Hacer la llamada usando la página de Playwright (mantiene cookies)
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
                    
                    // La respuesta viene en formato "0:{...}\\n1:{...}"
                    // Buscar la línea que contiene los datos
                    const lines = text.split('\\n');
                    for (const line of lines) {
                        if (line.startsWith('1:')) {
                            const jsonStr = line.substring(2);
                            return JSON.parse(jsonStr);
                        }
                    }
                    
                    return null;
                } catch (e) {
                    console.error('Error fetching history:', e);
                    return null;
                }
            }''', [uuid, date_range])
            
            return result
            
        except Exception as e:
            if self.debug:
                print(f"      [!] Error obteniendo histórico {uuid}: {e}")
            return None
    
    async def get_products(self, country: str = "CO", min_sales: int = 20, max_products: int = 100, max_pages: int = 5) -> List[Dict]:
        """Extrae productos de DropKiller con UUID"""
        print(f"  [2] Navegando a productos (ventas >= {min_sales})...")
        
        country_id = DROPKILLER_COUNTRIES.get(country, DROPKILLER_COUNTRIES["CO"])
        
        all_products = []
        seen_ids = set()
        consecutive_empty = 0
        
        try:
            for page_num in range(1, max_pages + 1):
                url = f"https://app.dropkiller.com/dashboard/products?country={country_id}&limit=50&page={page_num}&s7min={min_sales}"
                
                print(f"      Página {page_num}/{max_pages}...", end=" ", flush=True)
                await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await asyncio.sleep(4)
                
                for _ in range(3):
                    await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    await asyncio.sleep(0.5)
                await self.page.evaluate('window.scrollTo(0, 0)')
                await asyncio.sleep(1)
                
                # Extraer productos CON UUID
                page_products = await self.extract_products_with_uuid()
                
                new_count = 0
                for p in page_products:
                    pid = p.get('uuid', '')
                    if pid and pid not in seen_ids:
                        seen_ids.add(pid)
                        all_products.append(p)
                        new_count += 1
                
                print(f"→ {len(page_products)} extraídos, {new_count} nuevos | Total: {len(all_products)}")
                
                if new_count == 0:
                    consecutive_empty += 1
                    if consecutive_empty >= 2:
                        print(f"      ✓ Sin productos nuevos, terminando...")
                        break
                else:
                    consecutive_empty = 0
                
                if len(all_products) >= max_products:
                    print(f"      ✓ Alcanzado límite de {max_products} productos")
                    break
                
                if len(page_products) == 0:
                    print(f"      ✓ Página vacía, terminando...")
                    break
            
            all_products = [p for p in all_products if p.get('sales7d', 0) >= min_sales][:max_products]
            
            print(f"  [✓] Total: {len(all_products)} productos con UUID extraído")
            
            return all_products
            
        except Exception as e:
            print(f"  [✗] Error: {e}")
            import traceback
            traceback.print_exc()
            return all_products
    
    async def analyze_product_trends(self, products: List[Dict], max_history: int = 50) -> List[Dict]:
        """
        Obtiene y analiza el histórico de productos para determinar tendencias
        
        products: Lista de productos con UUID
        max_history: Máximo de productos a analizar histórico (para no sobrecargar)
        """
        print(f"\n  [3] Analizando histórico de {min(len(products), max_history)} productos...")
        
        analyzer = TrendAnalyzer()
        analyzed = []
        
        # Ordenar por ventas para priorizar los mejores
        sorted_products = sorted(products, key=lambda x: x.get('sales7d', 0), reverse=True)
        
        for i, product in enumerate(sorted_products[:max_history], 1):
            uuid = product.get('uuid')
            if not uuid:
                continue
            
            name = product.get('name', 'N/A')[:30]
            print(f"      [{i}/{min(len(products), max_history)}] {name}...", end=" ", flush=True)
            
            # Obtener histórico
            history_data = await self.get_product_history(uuid)
            
            if not history_data or 'data' not in history_data:
                print("Sin histórico")
                product['trend_pattern'] = 'NUEVO_SIN_DATOS'
                product['trend_score'] = 40
                product['is_growing'] = False
                analyzed.append(product)
                continue
            
            data = history_data['data']
            history = data.get('history', [])
            created_at = data.get('createdAt')
            
            # Analizar tendencia
            trend_result = analyzer.analyze_history(history, created_at)
            
            # Agregar datos al producto
            product['created_at'] = created_at
            product['total_sold'] = data.get('totalSoldUnits', 0)
            product['trend_pattern'] = trend_result['trend_pattern']
            product['trend_score'] = trend_result['trend_score']
            product['growth_rate_7d'] = trend_result['growth_rate_7d']
            product['growth_rate_30d'] = trend_result['growth_rate_30d']
            product['is_growing'] = trend_result['is_growing']
            product['avg_daily'] = trend_result['avg_daily']
            product['provider_name'] = data.get('provider', {}).get('name', 'N/A')
            product['category'] = data.get('baseCategory', {}).get('name', 'N/A')
            
            pattern = trend_result['trend_pattern']
            score = trend_result['trend_score']
            growth = trend_result['growth_rate_7d']
            
            emoji = "🚀" if pattern == "DESPEGANDO" else "📈" if pattern == "CRECIMIENTO_SOSTENIDO" else "📊" if pattern == "ESTABLE" else "📉" if pattern == "DECAYENDO" else "🎢"
            print(f"{emoji} {pattern} (Score:{score}, Growth7d:{growth:+.0f}%)")
            
            analyzed.append(product)
            
            # Pequeña pausa para no sobrecargar
            await asyncio.sleep(0.5)
        
        # Agregar productos no analizados
        for product in sorted_products[max_history:]:
            product['trend_pattern'] = 'NO_ANALIZADO'
            product['trend_score'] = 50
            product['is_growing'] = None
            analyzed.append(product)
        
        return analyzed

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
        "multiplier": round(optimal_price / cost_price, 1) if cost_price > 0 else 0,
    }


# ============== MAIN ==============
async def main():
    parser = argparse.ArgumentParser(description="DropKiller Scraper v5.0 con Análisis de Tendencia")
    parser.add_argument("--min-sales", type=int, default=30, help="Ventas mínimas 7d")
    parser.add_argument("--max-products", type=int, default=100, help="Máx productos a extraer")
    parser.add_argument("--max-history", type=int, default=50, help="Máx productos para análisis de histórico")
    parser.add_argument("--max-pages", type=int, default=5, help="Máx páginas")
    parser.add_argument("--country", default="CO", help="País")
    parser.add_argument("--visible", action="store_true", help="Mostrar navegador")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    args = parser.parse_args()
    
    if not DROPKILLER_EMAIL or not DROPKILLER_PASSWORD:
        print("ERROR: Falta DROPKILLER_EMAIL o DROPKILLER_PASSWORD en .env")
        sys.exit(1)
    
    print("=" * 70)
    print("  ESTRATEGAS IA - Scraper v5.0 | Análisis de Tendencia 6 Meses")
    print("=" * 70)
    print(f"  País: {args.country} | Ventas mín: {args.min_sales}")
    print(f"  Máx productos: {args.max_products} | Análisis histórico: {args.max_history}")
    print("=" * 70)
    
    scraper = DropKillerScraper(DROPKILLER_EMAIL, DROPKILLER_PASSWORD, debug=args.debug)
    supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
    
    stats = {"scraped": 0, "analyzed": 0, "growing": 0, "recommended": 0}
    
    try:
        print("\n[FASE 1] Login")
        await scraper.init_browser(headless=not args.visible)
        
        if not await scraper.login():
            print("\nERROR: Login fallido")
            return
        
        print("\n[FASE 2] Extracción de productos")
        products = await scraper.get_products(args.country, args.min_sales, args.max_products, args.max_pages)
        
        if not products:
            print("\nNo se encontraron productos.")
            return
        
        stats["scraped"] = len(products)
        
        # Analizar tendencias
        products = await scraper.analyze_product_trends(products, args.max_history)
        
        stats["analyzed"] = len([p for p in products if p.get('trend_pattern') != 'NO_ANALIZADO'])
        stats["growing"] = len([p for p in products if p.get('is_growing')])
        
        print(f"\n[FASE 4] Clasificación y Guardado")
        
        # Clasificar productos
        opportunities = []
        
        for product in products:
            margin = calculate_margin(product.get('providerPrice', 35000))
            
            pattern = product.get('trend_pattern', 'NO_ANALIZADO')
            trend_score = product.get('trend_score', 50)
            sales7d = product.get('sales7d', 0)
            roi = margin['roi']
            
            # Criterios de oportunidad
            is_opportunity = (
                pattern in ['DESPEGANDO', 'CRECIMIENTO_SOSTENIDO'] and
                trend_score >= 70 and
                sales7d >= 30 and
                roi >= 15
            )
            
            # También considerar estables con muy buenas métricas
            if pattern == 'ESTABLE' and trend_score >= 65 and sales7d >= 100 and roi >= 20:
                is_opportunity = True
            
            if is_opportunity:
                stats["recommended"] += 1
                opportunities.append(product)
            
            # Guardar en Supabase si está configurado
            if supabase:
                data = {
                    "external_id": product.get('uuid', ''),
                    "platform": "dropi",
                    "country_code": args.country,
                    "name": product.get('name', '')[:60],
                    "cost_price": product.get('providerPrice', 0),
                    "suggested_price": margin["optimal_price"],
                    "optimal_price": margin["optimal_price"],
                    "sales_7d": sales7d,
                    "sales_30d": product.get('sales30d', 0),
                    "current_stock": product.get('stock', 0),
                    "real_margin": margin["net_margin"],
                    "roi": roi,
                    "breakeven_price": margin["breakeven_price"],
                    "viability_score": trend_score,
                    "viability_verdict": pattern,
                    "trend_pattern": pattern,
                    "trend_score": trend_score,
                    "growth_rate_7d": product.get('growth_rate_7d', 0),
                    "growth_rate_30d": product.get('growth_rate_30d', 0),
                    "is_growing": product.get('is_growing', False),
                    "avg_daily_sales": product.get('avg_daily', 0),
                    "total_sold": product.get('total_sold', 0),
                    "created_at_product": product.get('created_at'),
                    "provider_name": product.get('provider_name', ''),
                    "category": product.get('category', ''),
                    "is_recommended": is_opportunity,
                    "analyzed_at": datetime.now().isoformat()
                }
                supabase.upsert("analyzed_products", data)
        
        # Resumen
        print("\n" + "=" * 70)
        print("  RESUMEN")
        print("=" * 70)
        print(f"  Productos scrapeados: {stats['scraped']}")
        print(f"  Analizados con histórico: {stats['analyzed']}")
        print(f"  En crecimiento: {stats['growing']}")
        print(f"  🎯 OPORTUNIDADES: {stats['recommended']}")
        
        # Mostrar oportunidades por categoría
        print("\n" + "=" * 70)
        print("  📊 CLASIFICACIÓN POR TENDENCIA")
        print("=" * 70)
        
        for pattern, description in TREND_PATTERNS.items():
            count = len([p for p in products if p.get('trend_pattern') == pattern])
            if count > 0:
                print(f"  {description}: {count}")
        
        # Top oportunidades
        if opportunities:
            print("\n" + "=" * 70)
            print("  🏆 TOP OPORTUNIDADES (Despegando + Creciendo)")
            print("=" * 70)
            
            # Ordenar por trend_score y ventas
            top = sorted(opportunities, key=lambda x: (x.get('trend_score', 0), x.get('sales7d', 0)), reverse=True)[:15]
            
            for i, p in enumerate(top, 1):
                name = p.get('name', 'N/A')[:35]
                pattern = p.get('trend_pattern', 'N/A')
                sales7d = p.get('sales7d', 0)
                growth = p.get('growth_rate_7d', 0)
                margin = calculate_margin(p.get('providerPrice', 35000))
                
                emoji = "🚀" if pattern == "DESPEGANDO" else "📈"
                print(f"  {i:2}. {emoji} {name}")
                print(f"      V7d:{sales7d} | Growth:{growth:+.0f}% | ROI:{margin['roi']}% | ${p.get('providerPrice', 0):,}")
        
        print("=" * 70)
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
