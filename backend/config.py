"""
Configuración de Estrategas IA Tools
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://dzfwbwwjeiocvtyjeoqf.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # anon key

# Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# DropKiller JWT (se pasa como argumento o env var)
DROPKILLER_JWT = os.getenv("DROPKILLER_JWT", "")

# Países soportados
COUNTRIES = {
    "CO": {
        "name": "Colombia",
        "dropkiller_id": "65c75a5f-0c4a-45fb-8c90-5b538805a15a",
        "adskiller_id": "10ba518f-80f3-4b8e-b9ba-1a8b62d40c47",
        "shipping_cost": 18000,
        "avg_cpa": 25000,
        "currency": "COP"
    },
    "MX": {
        "name": "México",
        "dropkiller_id": "98993bd0-955a-4fa3-9612-c9d4389c44d0",
        "adskiller_id": "40334494-86fc-4fc0-857a-281816247906",
        "shipping_cost": 150,
        "avg_cpa": 200,
        "currency": "MXN"
    },
    "EC": {
        "name": "Ecuador",
        "dropkiller_id": "82811e8b-d17d-4ab9-847a-fa925785d566",
        "adskiller_id": "1be5939b-f5b1-41ea-8546-fc72a7381c9d",
        "shipping_cost": 5,
        "avg_cpa": 8,
        "currency": "USD"
    }
}

# Filtros por defecto para búsqueda de productos
DEFAULT_FILTERS = {
    "min_sales_7d": 50,        # Mínimo 50 ventas en 7 días
    "min_stock": 30,           # Mínimo 30 unidades en stock
    "min_price": 20000,        # Precio mínimo del proveedor
    "max_price": 200000,       # Precio máximo del proveedor
    "min_margin_percent": 30,  # Mínimo 30% margen bruto
}

# Configuración de análisis
ANALYSIS_CONFIG = {
    "return_rate": 0.22,       # 22% tasa de devoluciones
    "cancel_rate": 0.15,       # 15% tasa de cancelaciones
    "min_viable_margin": 10000, # Mínimo $10,000 COP de margen neto para ser viable
    "min_viable_roi": 15,      # Mínimo 15% ROI para ser viable
}
