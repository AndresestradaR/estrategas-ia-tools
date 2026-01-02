# Estrategas IA Tools - Backend de Análisis

Sistema de análisis automatizado de productos para dropshipping.

## ¿Qué hace?

1. **Scrapea productos** de DropKiller con filtros (ventas, stock, precio)
2. **Busca competencia** en Adskiller (anuncios de Facebook/TikTok)
3. **Calcula margen REAL** (envío, CPA, devoluciones, cancelaciones)
4. **Analiza con Claude AI** para determinar viabilidad
5. **Guarda en Supabase** solo productos que valen la pena
6. **El frontend muestra** productos pre-analizados

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/AndresestradaR/estrategas-ia-tools.git
cd estrategas-ia-tools/backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o: venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

## Configuración de Supabase

1. Ve a [Supabase](https://supabase.com) y crea un proyecto
2. Ve a SQL Editor y ejecuta el contenido de `schema.sql`
3. Copia la URL y anon key del proyecto

## Uso

### Obtener JWT de DropKiller

1. Ve a [app.dropkiller.com](https://app.dropkiller.com)
2. Inicia sesión
3. Abre DevTools (F12) → Application → Cookies
4. Copia el valor de `__session`

**⚠️ El JWT expira en ~60 minutos**

### Ejecutar análisis

```bash
# Con JWT como argumento
python run.py --jwt="eyJ..." --country=CO --max=30 --min-sales=50

# O con variable de entorno
export DROPKILLER_JWT="eyJ..."
export ANTHROPIC_API_KEY="sk-ant-..."
python run.py
```

### Parámetros

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `--jwt` | JWT de DropKiller | env var |
| `--country` | Código país (CO, MX, EC) | CO |
| `--max` | Máximo productos a analizar | 30 |
| `--min-sales` | Ventas mínimas 7 días | 50 |

## Estructura

```
backend/
├── config.py      # Configuración y constantes
├── scraper.py     # Scrapers de DropKiller y Adskiller
├── analyzer.py    # Calculadora de margen y análisis IA
├── run.py         # Pipeline principal
├── schema.sql     # Schema de base de datos
└── requirements.txt
```

## Criterios de Recomendación

Un producto se recomienda si:
- Score de viabilidad ≥ 45
- ROI ≥ 10%
- Margen neto ≥ $5,000 COP
- La IA NO dice "NO_VENDER"
