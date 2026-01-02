'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, TrendingUp, TrendingDown, Package, DollarSign, 
  Loader2, BarChart3, Calendar, Store, ExternalLink, 
  Radar, Eye, Target, Zap, Users, Sparkles, ShoppingCart
} from 'lucide-react'
import { DROPKILLER_COUNTRIES } from '@/types'

interface Product {
  id: string
  externalId: string
  name: string
  slug: string
  image: string
  price: number
  salePrice: number
  stock: number
  platform: string
  country: string
  countryCode: string
  supplier: string
  supplierId: string
  createdAt: string
  updatedAt: string
  sales7d: number
  sales30d: number
  billing7d: number
  billing30d: number
  url?: string
}

interface ProductHistory {
  date: string
  stock: number
  billing: number
  salePrice: number
  soldUnits: number
  stockAdjustment: boolean
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

function ScoreBadge({ score }: { score: number }) {
  const getScoreColor = (s: number) => {
    if (s >= 8) return 'text-radar-accent bg-radar-accent/10 border-radar-accent/30'
    if (s >= 6) return 'text-radar-warning bg-radar-warning/10 border-radar-warning/30'
    return 'text-radar-danger bg-radar-danger/10 border-radar-danger/30'
  }

  const getScoreEmoji = (s: number) => {
    if (s >= 8) return '🟢'
    if (s >= 6) return '🟡'
    return '🔴'
  }

  return (
    <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border font-mono text-lg font-bold ${getScoreColor(score)}`}>
      <span>{getScoreEmoji(score)}</span>
      <span>{score.toFixed(1)}/10</span>
    </div>
  )
}

function calculateScore(product: Product): number {
  let score = 5
  
  if (product.sales7d > 500) score += 2
  else if (product.sales7d > 200) score += 1.5
  else if (product.sales7d > 100) score += 1
  else if (product.sales7d > 50) score += 0.5
  
  const weeklyRatio = product.sales30d > 0 ? (product.sales7d * 4) / product.sales30d : 0
  if (weeklyRatio > 1.5) score += 1.5
  else if (weeklyRatio > 1.2) score += 1
  else if (weeklyRatio < 0.7) score -= 1
  
  if (product.stock > 100 && product.stock < 5000) score += 0.5
  else if (product.stock < 50) score -= 0.5
  
  return Math.max(1, Math.min(10, score))
}

function getScoreExplanation(product: Product): string[] {
  const explanations: string[] = []
  
  if (product.sales7d > 500) {
    explanations.push(`🔥 Ventas altas: ${product.sales7d} unidades en 7 días`)
  } else if (product.sales7d > 200) {
    explanations.push(`📈 Ventas moderadas: ${product.sales7d} unidades en 7 días`)
  } else if (product.sales7d < 50) {
    explanations.push(`⚠️ Ventas bajas: solo ${product.sales7d} unidades en 7 días`)
  }
  
  const weeklyRatio = product.sales30d > 0 ? (product.sales7d * 4) / product.sales30d : 0
  if (weeklyRatio > 1.5) {
    explanations.push(`🚀 Tendencia: producto en crecimiento (+${Math.round((weeklyRatio - 1) * 100)}% vs promedio)`)
  } else if (weeklyRatio > 1.2) {
    explanations.push(`📊 Tendencia: crecimiento moderado`)
  } else if (weeklyRatio < 0.7) {
    explanations.push(`📉 Tendencia: ventas en descenso`)
  }
  
  const margin = ((product.salePrice - product.price) / product.salePrice) * 100
  if (margin > 50) {
    explanations.push(`💰 Margen excelente: ${margin.toFixed(0)}%`)
  } else if (margin > 30) {
    explanations.push(`💵 Margen aceptable: ${margin.toFixed(0)}%`)
  } else {
    explanations.push(`⚠️ Margen bajo: ${margin.toFixed(0)}%`)
  }
  
  if (product.stock > 1000) {
    explanations.push(`📦 Stock saludable: ${product.stock.toLocaleString()} unidades disponibles`)
  } else if (product.stock < 100) {
    explanations.push(`⚠️ Stock bajo: solo ${product.stock} unidades`)
  }
  
  return explanations
}

function getSalesAngles(product: Product): { angle: string; effectiveness: number }[] {
  const angles = []
  
  if (product.sales7d > 200) {
    angles.push({ angle: "Producto más vendido", effectiveness: 85 })
  }
  
  if (product.name.toLowerCase().includes('premium') || product.name.toLowerCase().includes('pro')) {
    angles.push({ angle: "Calidad premium", effectiveness: 78 })
  }
  
  const margin = ((product.salePrice - product.price) / product.salePrice) * 100
  if (margin > 40) {
    angles.push({ angle: "Precio especial / Oferta", effectiveness: 82 })
  }
  
  angles.push({ angle: "Envío rápido / Entrega garantizada", effectiveness: 75 })
  angles.push({ angle: "Satisfacción garantizada", effectiveness: 72 })
  
  return angles.slice(0, 4)
}

function StatCard({ label, value, icon: Icon, trend, subtext }: {
  label: string
  value: string | number
  icon: any
  trend?: 'up' | 'down' | 'neutral'
  subtext?: string
}) {
  return (
    <div className="bg-radar-card border border-radar-border rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{label}</span>
        <Icon className="w-5 h-5 text-radar-accent" />
      </div>
      <div className="flex items-center gap-2">
        <span className="text-2xl font-bold font-mono">{value}</span>
        {trend === 'up' && <TrendingUp className="w-5 h-5 text-radar-accent" />}
        {trend === 'down' && <TrendingDown className="w-5 h-5 text-radar-danger" />}
      </div>
      {subtext && <p className="text-xs text-gray-500 mt-1">{subtext}</p>}
    </div>
  )
}

export default function ProductDetailPage() {
  const params = useParams()
  const productId = params.id as string
  
  const [product, setProduct] = useState<Product | null>(null)
  const [history, setHistory] = useState<ProductHistory[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (productId) {
      fetchProductDetail()
    }
  }, [productId])

  async function fetchProductDetail() {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`/api/products/${productId}`)
      
      if (!response.ok) {
        throw new Error('Error al cargar el producto')
      }
      
      const data = await response.json()
      setProduct(data.product)
      setHistory(data.history || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
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
          <span className="ml-3 text-gray-400">Cargando producto...</span>
        </div>
      </div>
    )
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-radar-dark">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <Link href="/productos" className="inline-flex items-center gap-2 text-radar-accent mb-8 hover:underline">
            <ArrowLeft className="w-5 h-5" />
            Volver a productos
          </Link>
          <div className="bg-radar-danger/10 border border-radar-danger/30 rounded-lg p-8 text-center">
            <p className="text-radar-danger text-lg">{error || 'Producto no encontrado'}</p>
            <button 
              onClick={fetchProductDetail}
              className="mt-4 text-sm underline hover:no-underline"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    )
  }

  const score = calculateScore(product)
  const margin = Math.round(((product.salePrice - product.price) / product.salePrice) * 100)
  const country = DROPKILLER_COUNTRIES.find(c => c.id === product.country)
  const scoreExplanation = getScoreExplanation(product)
  const salesAngles = getSalesAngles(product)
  
  const countryFlags: Record<string, string> = {
    'CO': '🇨🇴', 'EC': '🇪🇨', 'MX': '🇲🇽', 'CL': '🇨🇱', 
    'ES': '🇪🇸', 'PE': '🇵🇪', 'PA': '🇵🇦', 'PY': '🇵🇾',
    'AR': '🇦🇷', 'GT': '🇬🇹'
  }

  const weeklyTrend = product.sales30d > 0 
    ? ((product.sales7d * 4) / product.sales30d - 1) * 100 
    : 0

  return (
    <div className="min-h-screen bg-radar-dark">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Back Button */}
        <Link href="/productos" className="inline-flex items-center gap-2 text-radar-accent mb-8 hover:underline">
          <ArrowLeft className="w-5 h-5" />
          Volver a productos
        </Link>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Image & Basic Info */}
          <div className="space-y-6">
            {/* Product Image */}
            <div className="relative aspect-square bg-radar-card border border-radar-border rounded-2xl overflow-hidden">
              {product.image ? (
                <img 
                  src={product.image} 
                  alt={product.name}
                  className="w-full h-full object-contain p-4"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-500">
                  <Package className="w-32 h-32" />
                </div>
              )}
              <div className="absolute top-4 left-4 bg-radar-dark/80 backdrop-blur-sm px-3 py-1.5 rounded-lg text-sm font-mono">
                {countryFlags[country?.code || 'CO']} {country?.name || 'N/A'}
              </div>
              <div className="absolute top-4 right-4">
                <ScoreBadge score={score} />
              </div>
              <div className="absolute bottom-4 left-4 bg-radar-accent text-radar-dark px-3 py-1.5 rounded-lg text-sm font-semibold capitalize">
                {product.platform}
              </div>
            </div>

            {/* Product Title & Supplier */}
            <div>
              <h1 className="text-2xl font-bold mb-2">{product.name}</h1>
              <div className="flex items-center gap-4 text-gray-400">
                <span className="flex items-center gap-1">
                  <Store className="w-4 h-4" />
                  {product.supplier}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {new Date(product.createdAt).toLocaleDateString('es-ES')}
                </span>
              </div>
            </div>

            {/* Price Info */}
            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Costo</div>
                  <div className="text-xl font-bold font-mono">${product.price?.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Venta</div>
                  <div className="text-xl font-bold font-mono text-radar-accent">${product.salePrice?.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Margen</div>
                  <div className={`text-xl font-bold font-mono ${margin > 40 ? 'text-radar-accent' : margin > 20 ? 'text-radar-warning' : 'text-radar-danger'}`}>
                    {margin}%
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              {product.url && (
                <a 
                  href={product.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 flex items-center justify-center gap-2 bg-radar-accent text-radar-dark font-semibold py-3 rounded-lg hover:bg-radar-accent/90 transition-colors"
                >
                  <ExternalLink className="w-5 h-5" />
                  Ver en {product.platform}
                </a>
              )}
              <Link 
                href={`/creativos?search=${encodeURIComponent(product.name.split(' ').slice(0, 3).join(' '))}`}
                className="flex-1 flex items-center justify-center gap-2 bg-radar-card border border-radar-border py-3 rounded-lg hover:border-radar-accent/50 transition-colors"
              >
                <Eye className="w-5 h-5" />
                Buscar creativos
              </Link>
            </div>
          </div>

          {/* Right Column - Analytics */}
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4">
              <StatCard 
                label="Ventas 7 días"
                value={product.sales7d?.toLocaleString() || 0}
                icon={ShoppingCart}
                trend={weeklyTrend > 10 ? 'up' : weeklyTrend < -10 ? 'down' : 'neutral'}
                subtext={weeklyTrend !== 0 ? `${weeklyTrend > 0 ? '+' : ''}${weeklyTrend.toFixed(0)}% vs promedio` : undefined}
              />
              <StatCard 
                label="Ventas 30 días"
                value={product.sales30d?.toLocaleString() || 0}
                icon={BarChart3}
              />
              <StatCard 
                label="Stock disponible"
                value={product.stock?.toLocaleString() || 0}
                icon={Package}
                subtext={product.stock < 100 ? '⚠️ Stock bajo' : undefined}
              />
              <StatCard 
                label="Facturación 7d"
                value={`$${(product.billing7d / 1000000).toFixed(1)}M`}
                icon={DollarSign}
              />
            </div>

            {/* Score Explanation */}
            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="flex items-center gap-2 text-radar-accent font-semibold mb-4">
                <Sparkles className="w-5 h-5" />
                ¿Por qué este score?
              </div>
              <ul className="space-y-3">
                {scoreExplanation.map((exp, i) => (
                  <li key={i} className="text-sm text-gray-300 leading-relaxed">
                    {exp}
                  </li>
                ))}
              </ul>
            </div>

            {/* Sales Angles */}
            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="flex items-center gap-2 text-radar-accent font-semibold mb-4">
                <Target className="w-5 h-5" />
                Ángulos de Venta Sugeridos
              </div>
              <div className="space-y-3">
                {salesAngles.map((angle, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-sm">{angle.angle}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-radar-border rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-radar-accent rounded-full"
                          style={{ width: `${angle.effectiveness}%` }}
                        />
                      </div>
                      <span className="text-xs font-mono text-radar-accent">{angle.effectiveness}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Target Audience */}
            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="flex items-center gap-2 text-radar-accent font-semibold mb-4">
                <Users className="w-5 h-5" />
                Audiencia Objetivo
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-radar-accent/10 text-radar-accent rounded-full text-sm">25-45 años</span>
                <span className="px-3 py-1 bg-radar-accent/10 text-radar-accent rounded-full text-sm">Intereses: {product.name.split(' ')[0]}</span>
                <span className="px-3 py-1 bg-radar-accent/10 text-radar-accent rounded-full text-sm">LATAM</span>
                <span className="px-3 py-1 bg-radar-accent/10 text-radar-accent rounded-full text-sm">E-commerce buyers</span>
              </div>
            </div>

            {/* Emotional Triggers */}
            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="flex items-center gap-2 text-radar-accent font-semibold mb-4">
                <Zap className="w-5 h-5" />
                Triggers Emocionales
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-radar-warning/10 text-radar-warning rounded-full text-sm">Urgencia</span>
                <span className="px-3 py-1 bg-radar-info/10 text-radar-info rounded-full text-sm">Confianza</span>
                <span className="px-3 py-1 bg-radar-accent/10 text-radar-accent rounded-full text-sm">Exclusividad</span>
                <span className="px-3 py-1 bg-purple-500/10 text-purple-400 rounded-full text-sm">Satisfacción</span>
              </div>
            </div>
          </div>
        </div>

        {/* Sales History Chart Placeholder */}
        {history.length > 0 && (
          <div className="mt-8 bg-radar-card border border-radar-border rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-radar-accent" />
              Historial de Ventas (últimos 30 días)
            </h3>
            <div className="h-64 flex items-end justify-between gap-1">
              {history.slice(-30).map((day, i) => (
                <div 
                  key={i}
                  className="flex-1 bg-radar-accent/20 hover:bg-radar-accent/40 rounded-t transition-colors cursor-pointer group relative"
                  style={{ 
                    height: `${Math.min(100, (day.soldUnits / Math.max(...history.map(h => h.soldUnits))) * 100)}%`,
                    minHeight: '4px'
                  }}
                  title={`${day.date}: ${day.soldUnits} ventas`}
                >
                  <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-radar-dark px-2 py-1 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                    {day.soldUnits} ventas
                  </div>
                </div>
              ))}
            </div>
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span>Hace 30 días</span>
              <span>Hoy</span>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
