# DropKiller Scraper - Estrategas IA

Scraper automático que extrae productos ganadores de DropKiller y los analiza.

## Requisitos

- Python 3.9+
- Playwright

## Instalación

```bash
pip install -r requirements.txt
playwright install chromium
```

## Variables de entorno

Crear archivo `.env`:

```env
# DropKiller
DROPKILLER_EMAIL=tu_email@gmail.com
DROPKILLER_PASSWORD=tu_password

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=tu_key_secreto

# Claude (opcional)
ANTHROPIC_API_KEY=sk-ant-xxx
```

## Uso

```bash
# Ejecutar scraper
python scraper_auto.py

# Con opciones
python scraper_auto.py --min-sales 20 --max-products 50 --country CO
```

## Deploy en Railway

1. Crear proyecto en Railway
2. Conectar este repo
3. Agregar variables de entorno
4. El cron se ejecuta cada 6 horas automáticamente

## Flujo

1. Login automático en DropKiller (Playwright)
2. Navegar a productos con filtros (ventas > 20, stock > 30)
3. Extraer IDs de productos del DOM
4. Consultar API pública para historial de ventas
5. Calcular márgenes y viabilidad
6. Analizar con Claude AI
7. Guardar en Supabase
