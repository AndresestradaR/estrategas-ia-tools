-- ============================================
-- ESTRATEGAS IA TOOLS - Database Schema
-- ============================================

-- Tabla principal de productos analizados
CREATE TABLE IF NOT EXISTS analyzed_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identificación
    external_id TEXT NOT NULL,              -- ID del producto en Dropi
    platform TEXT NOT NULL DEFAULT 'dropi', -- dropi, easydrop, etc
    country_code TEXT NOT NULL DEFAULT 'CO',
    
    -- Info básica
    name TEXT NOT NULL,
    image_url TEXT,
    supplier_name TEXT,
    
    -- Precios
    cost_price INTEGER NOT NULL,            -- Precio proveedor (COP)
    suggested_price INTEGER NOT NULL,       -- Precio sugerido venta
    optimal_price INTEGER,                  -- Precio óptimo calculado por IA
    
    -- Métricas de ventas
    sales_7d INTEGER DEFAULT 0,
    sales_30d INTEGER DEFAULT 0,
    billing_7d BIGINT DEFAULT 0,
    billing_30d BIGINT DEFAULT 0,
    current_stock INTEGER DEFAULT 0,
    
    -- Historial (JSON array de últimos 6 meses)
    sales_history JSONB,                    -- [{month: "Dic", sales: 1234}, ...]
    
    -- Análisis financiero
    shipping_cost INTEGER DEFAULT 18000,    -- Costo envío COD
    estimated_cpa INTEGER DEFAULT 25000,    -- CPA estimado
    return_rate DECIMAL(3,2) DEFAULT 0.22,  -- Tasa devoluciones (22%)
    cancel_rate DECIMAL(3,2) DEFAULT 0.15,  -- Tasa cancelaciones (15%)
    real_margin INTEGER,                    -- Margen neto real calculado
    roi DECIMAL(5,2),                       -- ROI %
    breakeven_price INTEGER,                -- Precio mínimo para no perder
    
    -- Score y viabilidad
    viability_score INTEGER,                -- 0-100
    viability_verdict TEXT,                 -- EXCELENTE, VIABLE, ARRIESGADO, NO_RECOMENDADO
    score_reasons JSONB,                    -- Array de razones del score
    
    -- Competencia (de Adskiller)
    competitors JSONB,                      -- Array de competidores con sus datos
    competitor_count INTEGER DEFAULT 0,
    avg_competitor_price INTEGER,
    min_competitor_price INTEGER,
    max_competitor_price INTEGER,
    
    -- Ángulos de venta
    used_angles JSONB,                      -- Ángulos ya usados por competencia
    unused_angles JSONB,                    -- Ángulos sin explotar (oportunidad)
    
    -- Análisis IA
    ai_analysis TEXT,                       -- Análisis completo de Claude
    ai_recommendation TEXT,                 -- Recomendación final
    target_audience JSONB,                  -- Audiencia objetivo
    emotional_triggers JSONB,               -- Triggers emocionales
    
    -- Trend
    trend_direction TEXT,                   -- UP, DOWN, STABLE
    trend_percentage DECIMAL(5,2),          -- % cambio 6 meses
    
    -- Metadata
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_recommended BOOLEAN DEFAULT FALSE,   -- Solo TRUE si vale la pena
    
    -- Unique constraint
    UNIQUE(external_id, platform, country_code)
);

-- Índices para búsquedas rápidas
CREATE INDEX IF NOT EXISTS idx_products_recommended ON analyzed_products(is_recommended) WHERE is_recommended = TRUE;
CREATE INDEX IF NOT EXISTS idx_products_score ON analyzed_products(viability_score DESC);
CREATE INDEX IF NOT EXISTS idx_products_country ON analyzed_products(country_code);
CREATE INDEX IF NOT EXISTS idx_products_sales ON analyzed_products(sales_7d DESC);

-- Tabla de competidores (detalle)
CREATE TABLE IF NOT EXISTS competitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES analyzed_products(id) ON DELETE CASCADE,
    
    -- Info del competidor
    page_name TEXT NOT NULL,
    company_name TEXT,
    ad_url TEXT,                            -- Link al anuncio en Meta Library
    store_url TEXT,                         -- Link a la tienda
    
    -- Precios y métricas
    sale_price INTEGER,
    
    -- Engagement
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    active_days INTEGER DEFAULT 0,
    
    -- Ángulo de venta
    main_angle TEXT,
    sales_angles JSONB,
    
    -- Media
    thumbnail_url TEXT,
    video_url TEXT,
    
    -- Análisis
    engagement_level TEXT,                  -- Alto, Medio, Bajo
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_competitors_product ON competitors(product_id);

-- Tabla de ejecuciones del pipeline
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'running',          -- running, completed, failed
    
    -- Stats
    products_scanned INTEGER DEFAULT 0,
    products_analyzed INTEGER DEFAULT 0,
    products_recommended INTEGER DEFAULT 0,
    
    -- Filtros usados
    filters_used JSONB,
    
    -- Errores
    error_message TEXT
);

-- Vista para productos recomendados (lo que muestra el frontend)
CREATE OR REPLACE VIEW recommended_products AS
SELECT 
    id,
    external_id,
    name,
    image_url,
    supplier_name,
    cost_price,
    suggested_price,
    optimal_price,
    sales_7d,
    sales_30d,
    current_stock,
    real_margin,
    roi,
    viability_score,
    viability_verdict,
    score_reasons,
    competitor_count,
    avg_competitor_price,
    unused_angles,
    ai_recommendation,
    trend_direction,
    trend_percentage,
    sales_history,
    analyzed_at
FROM analyzed_products
WHERE is_recommended = TRUE
ORDER BY viability_score DESC, sales_7d DESC;

-- Function para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
DROP TRIGGER IF EXISTS trigger_update_timestamp ON analyzed_products;
CREATE TRIGGER trigger_update_timestamp
    BEFORE UPDATE ON analyzed_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
