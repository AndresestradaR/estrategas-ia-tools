'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, TrendingUp, TrendingDown, Package, DollarSign, 
  Loader2, BarChart3, Calendar, Store, ExternalLink, 
  Radar, Eye, Target, Zap, Users, Sparkles, ShoppingCart, AlertCircle,
  AlertTriangle, CheckCircle, XCircle, Percent, Truck, MousePointer,
  RotateCcw, Calculator, TrendingUp as Trending, Users2, Lightbulb,
  LineChart
} from 'lucide-react'

const DROPKILLER_COUNTRIES = [
  { id: '65c75a5f-0c4a-45fb-8c90-5b538805a15a', name: 'Colombia', code: 'CO' },
  { id: '82811e8b-d17d-4ab9-847a-fa925785d566', name: 'Ecuador', code: 'EC' },
  { id: '98993bd0-955a-4fa3-9612-c9d4389c44d0', name: 'México', code: 'MX' },
]

// Demo products with REAL analysis
const DEMO_PRODUCTS: Record<string, any> = {
  'demo-1': {
    id: 'demo-1',
    name: 'Serum Vitamina C Premium Anti-edad',
    image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&h=600&fit=crop',
    price: 25000,
    salePrice: 65000,
    stock: 1250,
    platform: 'dropi',
    country: '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
    supplier: 'Beauty Supplier CO',
    sales7d: 847,
    sales30d: 2340,
    billing7d: 55000000,
    billing30d: 152000000,
    createdAt: '2025-10-15',
    // Historical data (6 months)
    salesHistory: [
      { month: 'Jul', sales: 1200 },
      { month: 'Ago', sales: 1450 },
      { month: 'Sep', sales: 1890 },
      { month: 'Oct', sales: 2100 },
      { month: 'Nov', sales: 2340 },
      { month: 'Dic', sales: 2680 },
    ],
    // Competition analysis
    competitors: [
      { name: 'Beauty Store CO', price: 69000, sales7d: 234, angle: 'Anti-manchas', engagement: 'Alto' },
      { name: 'Skincare Colombia', price: 59000, sales7d: 189, angle: 'Vitamina C pura', engagement: 'Medio' },
      { name: 'Glow Natural', price: 75000, sales7d: 156, angle: 'Resultados en 7 días', engagement: 'Alto' },
      { name: 'Dermashop', price: 65000, sales7d: 145, angle: 'Fórmula coreana', engagement: 'Bajo' },
      { name: 'Beauty Express', price: 55000, sales7d: 134, angle: 'Precio bajo', engagement: 'Medio' },
      { name: 'Natural Skin CO', price: 72000, sales7d: 98, angle: 'Ingredientes orgánicos', engagement: 'Alto' },
      { name: 'Face Care Plus', price: 68000, sales7d: 87, angle: 'Antes y después', engagement: 'Medio' },
      { name: 'Serum Shop', price: 62000, sales7d: 76, angle: 'Envío gratis', engagement: 'Bajo' },
    ],
    usedAngles: ['Anti-manchas', 'Vitamina C pura', 'Resultados en 7 días', 'Fórmula coreana', 'Precio bajo', 'Ingredientes orgánicos'],
    unusedAngles: ['Dermatológicamente probado', 'Usado por celebridades', 'Tecnología encapsulada', 'Apto para pieles sensibles', 'Concentración 20%'],
  },
  'demo-2': {
    id: 'demo-2',
    name: 'Faja Colombiana Reductora Premium',
    image: 'https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600&h=600&fit=crop',
    price: 35000,
    salePrice: 89000,
    stock: 890,
    platform: 'dropi',
    country: '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
    supplier: 'Moda Express',
    sales7d: 623,
    sales30d: 1890,
    billing7d: 55000000,
    billing30d: 168000000,
    createdAt: '2025-09-20',
    salesHistory: [
      { month: 'Jul', sales: 2100 },
      { month: 'Ago', sales: 2400 },
      { month: 'Sep', sales: 2200 },
      { month: 'Oct', sales: 1950 },
      { month: 'Nov', sales: 1890 },
      { month: 'Dic', sales: 1750 },
    ],
    competitors: [
      { name: 'Fajas Colombia', price: 95000, sales7d: 890, angle: 'Moldea al instante', engagement: 'Alto' },
      { name: 'Body Shapers', price: 85000, sales7d: 567, angle: 'Reduce 3 tallas', engagement: 'Alto' },
      { name: 'Moda Latina', price: 79000, sales7d: 445, angle: 'Postparto', engagement: 'Medio' },
      { name: 'Colombian Shape', price: 99000, sales7d: 389, angle: 'Calidad premium', engagement: 'Alto' },
      { name: 'Figura Perfecta', price: 75000, sales7d: 334, angle: 'Precio económico', engagement: 'Bajo' },
      { name: 'Slim Body CO', price: 92000, sales7d: 289, angle: 'Invisible bajo ropa', engagement: 'Medio' },
      { name: 'Fajas Express', price: 69000, sales7d: 256, angle: 'Envío mismo día', engagement: 'Bajo' },
      { name: 'Body Perfect', price: 88000, sales7d: 223, angle: 'Uso diario', engagement: 'Medio' },
      { name: 'Shape Colombia', price: 94000, sales7d: 198, angle: 'Resultados garantizados', engagement: 'Alto' },
      { name: 'Faja Queen', price: 82000, sales7d: 167, angle: 'La más vendida', engagement: 'Medio' },
    ],
    usedAngles: ['Moldea al instante', 'Reduce 3 tallas', 'Postparto', 'Calidad premium', 'Invisible bajo ropa', 'La más vendida'],
    unusedAngles: ['Transpirable / No da calor', 'Tallas grandes disponibles', 'Devolución gratis', 'Recomendada por cirujanos', 'Material colombiano certificado'],
  },
  'demo-3': {
    id: 'demo-3',
    name: 'Auriculares Bluetooth Pro TWS',
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=600&fit=crop',
    price: 28000,
    salePrice: 75000,
    stock: 2100,
    platform: 'dropi',
    country: '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
    supplier: 'Tech Imports',
    sales7d: 412,
    sales30d: 1456,
    billing7d: 30900000,
    billing30d: 109200000,
    createdAt: '2025-11-01',
    salesHistory: [
      { month: 'Jul', sales: 890 },
      { month: 'Ago', sales: 1100 },
      { month: 'Sep', sales: 1250 },
      { month: 'Oct', sales: 1400 },
      { month: 'Nov', sales: 1456 },
      { month: 'Dic', sales: 1520 },
    ],
    competitors: [
      { name: 'Tech Store CO', price: 79000, sales7d: 534, angle: 'Sonido HD', engagement: 'Alto' },
      { name: 'Audio Express', price: 69000, sales7d: 423, angle: '40 horas batería', engagement: 'Medio' },
      { name: 'Gadgets Plus', price: 85000, sales7d: 367, angle: 'Cancelación de ruido', engagement: 'Alto' },
      { name: 'Sound Colombia', price: 72000, sales7d: 298, angle: 'Deportivos', engagement: 'Medio' },
      { name: 'Audio Shop', price: 65000, sales7d: 245, angle: 'Precio bajo', engagement: 'Bajo' },
    ],
    usedAngles: ['Sonido HD', '40 horas batería', 'Cancelación de ruido', 'Deportivos', 'Resistente al agua'],
    unusedAngles: ['Gaming / Baja latencia', 'Carga inalámbrica', 'Control táctil', 'Asistente de voz', 'Modo transparencia'],
  },
  'demo-4': {
    id: 'demo-4',
    name: 'Plancha Alisadora Profesional',
    image: 'https://images.unsplash.com/photo-1522338242042-2d1c9cd60fc7?w=600&h=600&fit=crop',
    price: 45000,
    salePrice: 125000,
    stock: 567,
    platform: 'dropi',
    country: '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
    supplier: 'Beauty Tools',
    sales7d: 389,
    sales30d: 1234,
    billing7d: 48600000,
    billing30d: 154000000,
    createdAt: '2025-08-12',
    salesHistory: [
      { month: 'Jul', sales: 1450 },
      { month: 'Ago', sales: 1380 },
      { month: 'Sep', sales: 1320 },
      { month: 'Oct', sales: 1280 },
      { month: 'Nov', sales: 1234 },
      { month: 'Dic', sales: 1190 },
    ],
    competitors: [
      { name: 'Hair Pro CO', price: 135000, sales7d: 456, angle: 'Tecnología iónica', engagement: 'Alto' },
      { name: 'Beauty Tools', price: 119000, sales7d: 389, angle: 'Cerámica tourmalina', engagement: 'Medio' },
      { name: 'Style Express', price: 99000, sales7d: 312, angle: 'Calienta en 30 seg', engagement: 'Medio' },
      { name: 'Hair Care Plus', price: 145000, sales7d: 278, angle: 'Profesional de salón', engagement: 'Alto' },
    ],
    usedAngles: ['Tecnología iónica', 'Cerámica tourmalina', 'Calienta rápido', 'Profesional de salón'],
    unusedAngles: ['Sin daño por calor', 'Para todo tipo de cabello', 'Control digital de temperatura', 'Apagado automático', 'Cable giratorio 360°'],
  },
  'demo-5': {
    id: 'demo-5',
    name: 'Corrector de Postura Magnético',
    image: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=600&fit=crop',
    price: 18000,
    salePrice: 55000,
    stock: 3200,
    platform: 'dropi',
    country: '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
    supplier: 'Health Plus',
    sales7d: 1247,
    sales30d: 4890,
    billing7d: 68500000,
    billing30d: 268000000,
    createdAt: '2025-07-05',
    salesHistory: [
      { month: 'Jul', sales: 3200 },
      { month: 'Ago', sales: 3800 },
      { month: 'Sep', sales: 4200 },
      { month: 'Oct', sales: 4600 },
      { month: 'Nov', sales: 4890 },
      { month: 'Dic', sales: 5100 },
    ],
    competitors: [
      { name: 'Salud Express', price: 59000, sales7d: 1890, angle: 'Alivia dolor de espalda', engagement: 'Alto' },
      { name: 'Posture Pro', price: 49000, sales7d: 1456, angle: 'Discreto bajo ropa', engagement: 'Alto' },
      { name: 'Back Health', price: 65000, sales7d: 1123, angle: 'Recomendado por fisios', engagement: 'Alto' },
      { name: 'Corrector Plus', price: 45000, sales7d: 987, angle: 'Resultados en 1 semana', engagement: 'Medio' },
      { name: 'Health Store CO', price: 52000, sales7d: 834, angle: 'Magnético terapéutico', engagement: 'Medio' },
      { name: 'Bienestar Total', price: 58000, sales7d: 756, angle: 'Para trabajo de oficina', engagement: 'Alto' },
    ],
    usedAngles: ['Alivia dolor de espalda', 'Discreto bajo ropa', 'Recomendado por fisios', 'Resultados rápidos', 'Magnético'],
    unusedAngles: ['Mejora respiración', 'Aumenta confianza', 'Previene lesiones', 'Ajustable todas las tallas', 'Material transpirable'],
  },
  'demo-6': {
    id: 'demo-6',
    name: 'Kit Maquillaje Profesional 24pcs',
    image: 'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&h=600&fit=crop',
    price: 32000,
    salePrice: 85000,
    stock: 780,
    platform: 'dropi',
    country: '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
    supplier: 'Makeup Store',
    sales7d: 534,
    sales30d: 1678,
    billing7d: 45400000,
    billing30d: 142600000,
    createdAt: '2025-10-28',
    salesHistory: [
      { month: 'Jul', sales: 1100 },
      { month: 'Ago', sales: 1300 },
      { month: 'Sep', sales: 1450 },
      { month: 'Oct', sales: 1600 },
      { month: 'Nov', sales: 1678 },
      { month: 'Dic', sales: 1750 },
    ],
    competitors: [
      { name: 'Makeup Paradise', price: 89000, sales7d: 623, angle: 'Todo en un kit', engagement: 'Alto' },
      { name: 'Beauty Box CO', price: 79000, sales7d: 534, angle: 'Estuche premium', engagement: 'Medio' },
      { name: 'Cosméticos Express', price: 75000, sales7d: 456, angle: 'Brochas de calidad', engagement: 'Medio' },
      { name: 'Glow Makeup', price: 95000, sales7d: 389, angle: 'Colores vibrantes', engagement: 'Alto' },
    ],
    usedAngles: ['Todo en un kit', 'Estuche premium', 'Brochas de calidad', 'Colores vibrantes', 'Ahorra dinero'],
    unusedAngles: ['Tutoriales incluidos', 'Productos veganos', 'Ideal para principiantes', 'Colores para piel latina', 'Larga duración'],
  },
  'demo-7': {
    id: 'demo-7',
    name: 'Reloj Inteligente Deportivo',
    image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&h=600&fit=crop',
    price: 42000,
    salePrice: 95000,
    stock: 1450,
    platform: 'dropi',
    country: '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
    supplier: 'Smart Gadgets',
    sales7d: 756,
    sales30d: 2234,
    billing7d: 71800000,
    billing30d: 212000000,
    createdAt: '2025-11-15',
    salesHistory: [
      { month: 'Jul', sales: 1500 },
      { month: 'Ago', sales: 1750 },
      { month: 'Sep', sales: 1900 },
      { month: 'Oct', sales: 2100 },
      { month: 'Nov', sales: 2234 },
      { month: 'Dic', sales: 2400 },
    ],
    competitors: [
      { name: 'Tech Fitness', price: 99000, sales7d: 890, angle: 'Monitor cardíaco', engagement: 'Alto' },
      { name: 'Smart Watch CO', price: 89000, sales7d: 756, angle: 'Resistente al agua', engagement: 'Alto' },
      { name: 'Fitness Pro', price: 85000, sales7d: 623, angle: '15 modos deportivos', engagement: 'Medio' },
      { name: 'Wearable Store', price: 79000, sales7d: 534, angle: 'Batería 7 días', engagement: 'Medio' },
    ],
    usedAngles: ['Monitor cardíaco', 'Resistente al agua', 'Modos deportivos', 'Batería larga', 'Notificaciones'],
    unusedAngles: ['GPS integrado', 'Monitoreo de sueño', 'Pantalla AMOLED', 'Compatible iPhone/Android', 'Control de música'],
  },
  'demo-8': {
    id: 'demo-8',
    name: 'Lámpara LED Viral TikTok',
    image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=600&fit=crop',
    price: 22000,
    salePrice: 59000,
    stock: 2800,
    platform: 'dropi',
    country: '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
    supplier: 'Home Decor',
    sales7d: 923,
    sales30d: 3456,
    billing7d: 54400000,
    billing30d: 203900000,
    createdAt: '2025-12-01',
    salesHistory: [
      { month: 'Jul', sales: 800 },
      { month: 'Ago', sales: 1200 },
      { month: 'Sep', sales: 2100 },
      { month: 'Oct', sales: 2800 },
      { month: 'Nov', sales: 3456 },
      { month: 'Dic', sales: 3800 },
    ],
    competitors: [
      { name: 'LED Viral', price: 65000, sales7d: 1234, angle: 'Viral en TikTok', engagement: 'Alto' },
      { name: 'Deco Light', price: 55000, sales7d: 923, angle: '16 colores', engagement: 'Alto' },
      { name: 'Neon Store', price: 49000, sales7d: 756, angle: 'Control remoto', engagement: 'Medio' },
      { name: 'Ambient CO', price: 69000, sales7d: 623, angle: 'Para gaming', engagement: 'Alto' },
    ],
    usedAngles: ['Viral en TikTok', '16 colores', 'Control remoto', 'Para gaming', 'Ambiente aesthetic'],
    unusedAngles: ['Sincroniza con música', 'App de control', 'Ahorro de energía', 'Para streams/content', 'Regalo perfecto'],
  },
}

interface Product {
  id: string
  name: string
  image: string
  price: number
  salePrice: number
  stock: number
  platform: string
  country: string
  supplier: string
  sales7d: number
  sales30d: number
  billing7d: number
  billing30d: number
  createdAt: string
  salesHistory?: { month: string; sales: number }[]
  competitors?: { name: string; price: number; sales7d: number; angle: string; engagement: string }[]
  usedAngles?: string[]
  unusedAngles?: string[]
}

// REAL margin calculation
interface MarginAnalysis {
  precioVenta: number
  costoProducto: number
  costoEnvio: number
  cpaEstimado: number
  perdidaDevoluciones: number
  margenBruto: number
  margenNeto: number
  roi: number
  rentable: boolean
  breakeven: number
  gananciaEsperada: number
}

function calculateRealMargin(product: Product, cpaEstimado: number = 25000): MarginAnalysis {
  const precioVenta = product.salePrice
  const costoProducto = product.price
  const costoEnvio = 18000 // Promedio Colombia COD
  const tasaDevolucion = 0.22 // 22% promedio
  
  // Ingresos ajustados por devoluciones
  const ventasEfectivas = 1 - tasaDevolucion
  const ingresoEfectivo = precioVenta * ventasEfectivas
  
  // Costos por venta efectiva (pagamos envío siempre, devolución también cuesta)
  const costoDevolucion = precioVenta * tasaDevolucion * 0.3 // ~30% del precio se pierde en devolución
  const costoTotal = costoProducto + costoEnvio + cpaEstimado + costoDevolucion
  
  const margenBruto = precioVenta - costoProducto
  const margenNeto = ingresoEfectivo - costoTotal
  const roi = (margenNeto / costoTotal) * 100
  
  // Breakeven: ¿A cuánto tendría que vender para no perder?
  const breakeven = Math.ceil((costoTotal) / ventasEfectivas)
  
  // Ganancia esperada por cada 100 ventas
  const gananciaEsperada = margenNeto * 100
  
  return {
    precioVenta,
    costoProducto,
    costoEnvio,
    cpaEstimado,
    perdidaDevoluciones: Math.round(costoDevolucion),
    margenBruto,
    margenNeto: Math.round(margenNeto),
    roi: Math.round(roi),
    rentable: margenNeto > 5000, // Al menos $5,000 de ganancia
    breakeven,
    gananciaEsperada: Math.round(gananciaEsperada)
  }
}

function calculateViabilityScore(product: Product, margin: MarginAnalysis): { score: number; reasons: string[]; verdict: string } {
  let score = 0
  const reasons: string[] = []
  
  // 1. Rentabilidad (40 puntos)
  if (margin.roi > 30) {
    score += 40
    reasons.push(`✅ ROI excelente: ${margin.roi}%`)
  } else if (margin.roi > 15) {
    score += 25
    reasons.push(`🟡 ROI aceptable: ${margin.roi}%`)
  } else if (margin.roi > 0) {
    score += 10
    reasons.push(`⚠️ ROI bajo: ${margin.roi}% - Margen muy ajustado`)
  } else {
    score += 0
    reasons.push(`❌ ROI negativo: ${margin.roi}% - PÉRDIDA por venta`)
  }
  
  // 2. Tendencia de ventas (20 puntos)
  if (product.salesHistory) {
    const firstMonth = product.salesHistory[0].sales
    const lastMonth = product.salesHistory[product.salesHistory.length - 1].sales
    const growth = ((lastMonth - firstMonth) / firstMonth) * 100
    
    if (growth > 50) {
      score += 20
      reasons.push(`🚀 Tendencia: Crecimiento fuerte (+${growth.toFixed(0)}% en 6 meses)`)
    } else if (growth > 20) {
      score += 15
      reasons.push(`📈 Tendencia: Crecimiento moderado (+${growth.toFixed(0)}%)`)
    } else if (growth > 0) {
      score += 10
      reasons.push(`📊 Tendencia: Crecimiento leve (+${growth.toFixed(0)}%)`)
    } else {
      score += 0
      reasons.push(`📉 Tendencia: En descenso (${growth.toFixed(0)}%) - Producto en declive`)
    }
  }
  
  // 3. Nivel de competencia (20 puntos)
  const numCompetitors = product.competitors?.length || 0
  if (numCompetitors <= 3) {
    score += 20
    reasons.push(`🎯 Competencia baja: Solo ${numCompetitors} competidores activos`)
  } else if (numCompetitors <= 6) {
    score += 12
    reasons.push(`⚠️ Competencia media: ${numCompetitors} competidores - Requiere diferenciación`)
  } else {
    score += 5
    reasons.push(`🔴 Mercado saturado: ${numCompetitors}+ competidores - Difícil destacar`)
  }
  
  // 4. Volumen de ventas validado (10 puntos)
  if (product.sales7d > 500) {
    score += 10
    reasons.push(`✅ Demanda validada: ${product.sales7d.toLocaleString()} ventas/semana`)
  } else if (product.sales7d > 200) {
    score += 7
    reasons.push(`🟡 Demanda moderada: ${product.sales7d.toLocaleString()} ventas/semana`)
  } else {
    score += 3
    reasons.push(`⚠️ Demanda baja: ${product.sales7d} ventas/semana`)
  }
  
  // 5. Potencial de diferenciación (10 puntos)
  const unusedAngles = product.unusedAngles?.length || 0
  if (unusedAngles >= 4) {
    score += 10
    reasons.push(`💡 ${unusedAngles} ángulos sin explotar - Alto potencial de diferenciación`)
  } else if (unusedAngles >= 2) {
    score += 6
    reasons.push(`💡 ${unusedAngles} ángulos disponibles para diferenciarte`)
  } else {
    score += 2
    reasons.push(`⚠️ Pocos ángulos nuevos disponibles`)
  }
  
  // Veredicto final
  let verdict: string
  if (score >= 80) {
    verdict = '🟢 EXCELENTE - Alta probabilidad de éxito'
  } else if (score >= 60) {
    verdict = '🟡 VIABLE - Requiere buena ejecución'
  } else if (score >= 40) {
    verdict = '🟠 ARRIESGADO - Solo con diferenciación fuerte'
  } else {
    verdict = '🔴 NO RECOMENDADO - Alta probabilidad de pérdida'
  }
  
  return { score, reasons, verdict }
}

function Header() {
  return (
    <header className="border-b border-radar-border bg-radar-dark/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <Radar className="w-10 h-10 text-radar-accent" />
            <div>
              <h1 className="text-xl font-bold gradient-text">Estrategas IA</h1>
              <p className="text-xs text-gray-500">by Trucos Ecomm & Drop</p>
            </div>
          </Link>

          <nav className="flex items-center gap-6">
            <Link href="/productos" className="text-gray-400 hover:text-radar-accent transition-colors flex items-center gap-2">
              <Package className="w-4 h-4" />
              Productos
            </Link>
            <Link href="/creativos" className="text-gray-400 hover:text-radar-accent transition-colors flex items-center gap-2">
              <Eye className="w-4 h-4" />
              Creativos
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}

function SalesChart({ data }: { data: { month: string; sales: number }[] }) {
  const maxSales = Math.max(...data.map(d => d.sales))
  const minSales = Math.min(...data.map(d => d.sales))
  const trend = data[data.length - 1].sales > data[0].sales ? 'up' : 'down'
  
  return (
    <div className="bg-radar-card border border-radar-border rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <LineChart className="w-5 h-5 text-radar-accent" />
          Historial de Ventas (6 meses)
        </h3>
        <span className={`text-sm font-medium ${trend === 'up' ? 'text-radar-accent' : 'text-radar-danger'}`}>
          {trend === 'up' ? '↑' : '↓'} {Math.abs(Math.round(((data[data.length-1].sales - data[0].sales) / data[0].sales) * 100))}%
        </span>
      </div>
      
      <div className="flex items-end justify-between gap-2 h-40">
        {data.map((d, i) => {
          const height = ((d.sales - minSales * 0.8) / (maxSales - minSales * 0.8)) * 100
          const isLast = i === data.length - 1
          return (
            <div key={d.month} className="flex-1 flex flex-col items-center gap-2">
              <span className="text-xs font-mono text-gray-400">{(d.sales / 1000).toFixed(1)}k</span>
              <div 
                className={`w-full rounded-t transition-all ${isLast ? 'bg-radar-accent' : 'bg-radar-accent/40'}`}
                style={{ height: `${Math.max(height, 10)}%` }}
              />
              <span className="text-xs text-gray-500">{d.month}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function CompetitorTable({ competitors, currentPrice }: { competitors: any[]; currentPrice: number }) {
  const avgPrice = competitors.reduce((sum, c) => sum + c.price, 0) / competitors.length
  
  return (
    <div className="bg-radar-card border border-radar-border rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Users2 className="w-5 h-5 text-radar-accent" />
          Análisis de Competencia ({competitors.length} competidores)
        </h3>
        <span className="text-sm text-gray-400">
          Precio promedio: <span className="text-white font-mono">${avgPrice.toLocaleString()}</span>
        </span>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-radar-border text-left text-gray-400">
              <th className="pb-2 font-medium">Competidor</th>
              <th className="pb-2 font-medium">Precio</th>
              <th className="pb-2 font-medium">Ventas 7d</th>
              <th className="pb-2 font-medium">Ángulo principal</th>
              <th className="pb-2 font-medium">Engagement</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-radar-border">
            {competitors.slice(0, 8).map((c, i) => (
              <tr key={i} className="hover:bg-radar-dark/30">
                <td className="py-2 font-medium">{c.name}</td>
                <td className={`py-2 font-mono ${c.price < currentPrice ? 'text-radar-danger' : c.price > currentPrice ? 'text-radar-accent' : ''}`}>
                  ${c.price.toLocaleString()}
                </td>
                <td className="py-2 font-mono">{c.sales7d}</td>
                <td className="py-2 text-gray-400">{c.angle}</td>
                <td className="py-2">
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    c.engagement === 'Alto' ? 'bg-radar-accent/10 text-radar-accent' :
                    c.engagement === 'Medio' ? 'bg-radar-warning/10 text-radar-warning' :
                    'bg-gray-500/10 text-gray-400'
                  }`}>
                    {c.engagement}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {competitors.length > 8 && (
        <p className="text-xs text-gray-500 mt-3">+{competitors.length - 8} competidores más...</p>
      )}
    </div>
  )
}

export default function ProductDetailPage() {
  const params = useParams()
  const productId = params.id as string
  
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [cpaInput, setCpaInput] = useState(25000)

  useEffect(() => {
    if (productId) {
      fetchProductDetail()
    }
  }, [productId])

  async function fetchProductDetail() {
    setLoading(true)
    
    if (productId.startsWith('demo-')) {
      const demoProduct = DEMO_PRODUCTS[productId]
      if (demoProduct) {
        setProduct(demoProduct)
        setLoading(false)
        return
      }
    }
    
    try {
      const response = await fetch(`/api/products/${productId}`)
      if (!response.ok) throw new Error('API error')
      const data = await response.json()
      if (data.product) {
        setProduct(data.product)
      } else {
        throw new Error('No product')
      }
    } catch (err) {
      const demoProduct = DEMO_PRODUCTS[productId] || DEMO_PRODUCTS['demo-1']
      setProduct(demoProduct)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-radar-dark">
        <Header />
        <div className="flex items-center justify-center py-32">
          <Loader2 className="w-8 h-8 text-radar-accent animate-spin" />
          <span className="ml-3 text-gray-400">Analizando producto...</span>
        </div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-radar-dark">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <Link href="/productos" className="inline-flex items-center gap-2 text-radar-accent mb-8 hover:underline">
            <ArrowLeft className="w-5 h-5" />
            Volver a productos
          </Link>
          <div className="bg-radar-danger/10 border border-radar-danger/30 rounded-lg p-8 text-center">
            <p className="text-radar-danger text-lg">Producto no encontrado</p>
          </div>
        </div>
      </div>
    )
  }

  const margin = calculateRealMargin(product, cpaInput)
  const viability = calculateViabilityScore(product, margin)
  const country = DROPKILLER_COUNTRIES.find(c => c.id === product.country)
  
  const countryFlags: Record<string, string> = {
    'CO': '🇨🇴', 'EC': '🇪🇨', 'MX': '🇲🇽', 'CL': '🇨🇱', 
    'ES': '🇪🇸', 'PE': '🇵🇪', 'PA': '🇵🇦', 'PY': '🇵🇾',
    'AR': '🇦🇷', 'GT': '🇬🇹'
  }

  return (
    <div className="min-h-screen bg-radar-dark">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Link href="/productos" className="inline-flex items-center gap-2 text-radar-accent mb-6 hover:underline">
          <ArrowLeft className="w-5 h-5" />
          Volver a productos
        </Link>

        {/* Viability Score Banner */}
        <div className={`rounded-xl p-6 mb-8 ${
          viability.score >= 60 ? 'bg-radar-accent/10 border border-radar-accent/30' :
          viability.score >= 40 ? 'bg-radar-warning/10 border border-radar-warning/30' :
          'bg-radar-danger/10 border border-radar-danger/30'
        }`}>
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-4xl font-bold font-mono">{viability.score}</span>
                <span className="text-gray-400">/100</span>
                <span className={`text-lg font-semibold ${
                  viability.score >= 60 ? 'text-radar-accent' :
                  viability.score >= 40 ? 'text-radar-warning' :
                  'text-radar-danger'
                }`}>
                  {viability.verdict}
                </span>
              </div>
              <p className="text-sm text-gray-400">Score de Viabilidad - Análisis completo del producto</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">Margen Neto Estimado</div>
              <div className={`text-2xl font-bold font-mono ${margin.margenNeto > 0 ? 'text-radar-accent' : 'text-radar-danger'}`}>
                ${margin.margenNeto.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">por venta efectiva</div>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Product Info */}
          <div className="space-y-6">
            <div className="relative aspect-square bg-radar-card border border-radar-border rounded-2xl overflow-hidden">
              {product.image && (
                <img 
                  src={product.image} 
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              )}
              <div className="absolute top-4 left-4 bg-radar-dark/80 backdrop-blur-sm px-3 py-1.5 rounded-lg text-sm font-mono">
                {countryFlags[country?.code || 'CO']} {country?.name || 'Colombia'}
              </div>
              <div className="absolute bottom-4 left-4 bg-radar-accent text-radar-dark px-3 py-1.5 rounded-lg text-sm font-semibold capitalize">
                {product.platform}
              </div>
            </div>

            <div>
              <h1 className="text-xl font-bold mb-2">{product.name}</h1>
              <div className="flex items-center gap-4 text-sm text-gray-400">
                <span className="flex items-center gap-1">
                  <Store className="w-4 h-4" />
                  {product.supplier}
                </span>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-radar-card border border-radar-border rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">Ventas 7d</div>
                <div className="text-xl font-bold font-mono text-radar-accent">{product.sales7d.toLocaleString()}</div>
              </div>
              <div className="bg-radar-card border border-radar-border rounded-lg p-3">
                <div className="text-xs text-gray-400 mb-1">Stock</div>
                <div className="text-xl font-bold font-mono">{product.stock.toLocaleString()}</div>
              </div>
            </div>
          </div>

          {/* Middle Column - Financial Analysis */}
          <div className="space-y-6">
            {/* ROI Calculator */}
            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <h3 className="font-semibold flex items-center gap-2 mb-4">
                <Calculator className="w-5 h-5 text-radar-accent" />
                Calculadora de Rentabilidad REAL
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-radar-border">
                  <span className="text-gray-400 flex items-center gap-2">
                    <DollarSign className="w-4 h-4" /> Precio de venta
                  </span>
                  <span className="font-mono font-bold">${margin.precioVenta.toLocaleString()}</span>
                </div>
                
                <div className="flex justify-between items-center py-2 border-b border-radar-border">
                  <span className="text-gray-400 flex items-center gap-2">
                    <Package className="w-4 h-4" /> Costo producto
                  </span>
                  <span className="font-mono text-radar-danger">-${margin.costoProducto.toLocaleString()}</span>
                </div>
                
                <div className="flex justify-between items-center py-2 border-b border-radar-border">
                  <span className="text-gray-400 flex items-center gap-2">
                    <Truck className="w-4 h-4" /> Costo envío (COD)
                  </span>
                  <span className="font-mono text-radar-danger">-${margin.costoEnvio.toLocaleString()}</span>
                </div>
                
                <div className="flex justify-between items-center py-2 border-b border-radar-border">
                  <span className="text-gray-400 flex items-center gap-2">
                    <MousePointer className="w-4 h-4" /> CPA estimado
                    <input 
                      type="number" 
                      value={cpaInput}
                      onChange={(e) => setCpaInput(parseInt(e.target.value) || 0)}
                      className="w-20 bg-radar-dark border border-radar-border rounded px-2 py-1 text-xs font-mono ml-2"
                    />
                  </span>
                  <span className="font-mono text-radar-danger">-${margin.cpaEstimado.toLocaleString()}</span>
                </div>
                
                <div className="flex justify-between items-center py-2 border-b border-radar-border">
                  <span className="text-gray-400 flex items-center gap-2">
                    <RotateCcw className="w-4 h-4" /> Pérdida devoluciones (~22%)
                  </span>
                  <span className="font-mono text-radar-danger">-${margin.perdidaDevoluciones.toLocaleString()}</span>
                </div>
                
                <div className={`flex justify-between items-center py-3 rounded-lg px-3 ${margin.margenNeto > 0 ? 'bg-radar-accent/10' : 'bg-radar-danger/10'}`}>
                  <span className="font-semibold">MARGEN NETO</span>
                  <span className={`font-mono font-bold text-xl ${margin.margenNeto > 0 ? 'text-radar-accent' : 'text-radar-danger'}`}>
                    ${margin.margenNeto.toLocaleString()}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className="text-center p-3 bg-radar-dark/50 rounded-lg">
                    <div className="text-xs text-gray-400">ROI</div>
                    <div className={`font-mono font-bold ${margin.roi > 0 ? 'text-radar-accent' : 'text-radar-danger'}`}>
                      {margin.roi}%
                    </div>
                  </div>
                  <div className="text-center p-3 bg-radar-dark/50 rounded-lg">
                    <div className="text-xs text-gray-400">Breakeven</div>
                    <div className="font-mono font-bold">${margin.breakeven.toLocaleString()}</div>
                  </div>
                </div>
                
                <div className={`text-center p-3 rounded-lg ${margin.rentable ? 'bg-radar-accent/10 text-radar-accent' : 'bg-radar-danger/10 text-radar-danger'}`}>
                  {margin.rentable ? (
                    <span className="flex items-center justify-center gap-2">
                      <CheckCircle className="w-5 h-5" />
                      Producto potencialmente rentable
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      <XCircle className="w-5 h-5" />
                      ⚠️ Margen insuficiente - Riesgo de pérdida
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Score Breakdown */}
            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <h3 className="font-semibold flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-radar-accent" />
                ¿Por qué este score?
              </h3>
              <ul className="space-y-2">
                {viability.reasons.map((reason, i) => (
                  <li key={i} className="text-sm leading-relaxed">{reason}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Right Column - Opportunities */}
          <div className="space-y-6">
            {/* Unused Angles */}
            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <h3 className="font-semibold flex items-center gap-2 mb-4">
                <Lightbulb className="w-5 h-5 text-radar-accent" />
                Ángulos SIN Explotar
              </h3>
              <p className="text-xs text-gray-400 mb-3">Oportunidades de diferenciación vs la competencia</p>
              <div className="space-y-2">
                {product.unusedAngles?.map((angle, i) => (
                  <div key={i} className="flex items-center gap-2 p-2 bg-radar-accent/5 border border-radar-accent/20 rounded-lg">
                    <span className="text-radar-accent">💡</span>
                    <span className="text-sm">{angle}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Used Angles by Competition */}
            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <h3 className="font-semibold flex items-center gap-2 mb-4">
                <Target className="w-5 h-5 text-gray-400" />
                Ángulos Ya Usados
              </h3>
              <p className="text-xs text-gray-400 mb-3">La competencia ya los está usando</p>
              <div className="flex flex-wrap gap-2">
                {product.usedAngles?.map((angle, i) => (
                  <span key={i} className="px-3 py-1 bg-gray-500/10 text-gray-400 rounded-full text-xs">
                    {angle}
                  </span>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-3">
              <Link 
                href={`/creativos?search=${encodeURIComponent(product.name.split(' ').slice(0, 2).join(' '))}`}
                className="w-full flex items-center justify-center gap-2 bg-radar-accent text-radar-dark font-semibold py-3 rounded-lg hover:bg-radar-accent/90 transition-colors"
              >
                <Eye className="w-5 h-5" />
                Ver creativos de la competencia
              </Link>
              <button className="w-full flex items-center justify-center gap-2 bg-radar-card border border-radar-border py-3 rounded-lg hover:border-radar-accent/50 transition-colors">
                <ExternalLink className="w-5 h-5" />
                Ver en {product.platform}
              </button>
            </div>
          </div>
        </div>

        {/* Sales History Chart */}
        {product.salesHistory && (
          <div className="mt-8">
            <SalesChart data={product.salesHistory} />
          </div>
        )}

        {/* Competition Table */}
        {product.competitors && product.competitors.length > 0 && (
          <div className="mt-8">
            <CompetitorTable competitors={product.competitors} currentPrice={product.salePrice} />
          </div>
        )}
      </main>
    </div>
  )
}
