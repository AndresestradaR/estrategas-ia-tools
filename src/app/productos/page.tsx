'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  Search, Filter, TrendingUp, Package, DollarSign, 
  ChevronLeft, ChevronRight, Loader2, X, SlidersHorizontal,
  Radar, Eye, Zap, Globe, BarChart3, AlertCircle
} from 'lucide-react'

// Countries and platforms config
const DROPKILLER_COUNTRIES = [
  { id: '65c75a5f-0c4a-45fb-8c90-5b538805a15a', name: 'Colombia', code: 'CO' },
  { id: '82811e8b-d17d-4ab9-847a-fa925785d566', name: 'Ecuador', code: 'EC' },
  { id: '98993bd0-955a-4fa3-9612-c9d4389c44d0', name: 'México', code: 'MX' },
  { id: 'ad63080c-908d-4757-9548-30decb082b7e', name: 'Chile', code: 'CL' },
  { id: '3f18ae66-2f98-4af1-860e-53ed93e5cde0', name: 'España', code: 'ES' },
  { id: '6acfee32-9c25-4f95-b030-a005e488f3fb', name: 'Perú', code: 'PE' },
  { id: 'c1f01c6a-99c7-4253-b67f-4e2607efae9e', name: 'Panamá', code: 'PA' },
  { id: 'f2594db9-caee-4221-b4a6-9b6267730a2d', name: 'Paraguay', code: 'PY' },
  { id: 'de93b0dd-d9d3-468d-8c44-e9780799a29f', name: 'Argentina', code: 'AR' },
  { id: '77c15189-b3b9-4f55-9226-e56c231f87ac', name: 'Guatemala', code: 'GT' },
]

const PLATFORMS = ['dropi', 'easydrop', 'aliclick', 'dropea', 'droplatam', 'seventy block', 'wimpy', 'mastershop']

// Demo data for when API fails
const DEMO_PRODUCTS = [
  {
    id: 'demo-1',
    name: 'Serum Vitamina C Premium Anti-edad',
    image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&h=400&fit=crop',
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
  },
  {
    id: 'demo-2',
    name: 'Faja Colombiana Reductora Premium',
    image: 'https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=400&h=400&fit=crop',
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
  },
  {
    id: 'demo-3',
    name: 'Auriculares Bluetooth Pro TWS',
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',
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
  },
  {
    id: 'demo-4',
    name: 'Plancha Alisadora Profesional',
    image: 'https://images.unsplash.com/photo-1522338242042-2d1c9cd60fc7?w=400&h=400&fit=crop',
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
  },
  {
    id: 'demo-5',
    name: 'Corrector de Postura Magnético',
    image: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop',
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
  },
  {
    id: 'demo-6',
    name: 'Kit Maquillaje Profesional 24pcs',
    image: 'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=400&h=400&fit=crop',
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
  },
  {
    id: 'demo-7',
    name: 'Reloj Inteligente Deportivo',
    image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
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
  },
  {
    id: 'demo-8',
    name: 'Lámpara LED Viral TikTok',
    image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop',
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
  },
]

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
}

function Header() {
  return (
    <header className="border-b border-radar-border bg-radar-dark/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="relative">
              <Radar className="w-10 h-10 text-radar-accent" />
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">Estrategas IA</h1>
              <p className="text-xs text-gray-500">by Trucos Ecomm & Drop</p>
            </div>
          </Link>

          <nav className="flex items-center gap-6">
            <Link href="/productos" className="text-radar-accent font-medium flex items-center gap-2">
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
    <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full border font-mono text-xs font-bold ${getScoreColor(score)}`}>
      <span>{getScoreEmoji(score)}</span>
      <span>{score.toFixed(1)}</span>
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

function ProductCard({ product }: { product: Product }) {
  const score = calculateScore(product)
  const margin = Math.round(((product.salePrice - product.price) / product.salePrice) * 100)
  const country = DROPKILLER_COUNTRIES.find(c => c.id === product.country)
  
  const countryFlags: Record<string, string> = {
    'CO': '🇨🇴', 'EC': '🇪🇨', 'MX': '🇲🇽', 'CL': '🇨🇱', 
    'ES': '🇪🇸', 'PE': '🇵🇪', 'PA': '🇵🇦', 'PY': '🇵🇾',
    'AR': '🇦🇷', 'GT': '🇬🇹'
  }

  return (
    <Link href={`/productos/${product.id}`}>
      <div className="bg-radar-card border border-radar-border rounded-xl overflow-hidden transition-all duration-300 hover:border-radar-accent/50 hover:shadow-lg hover:shadow-radar-accent/10 cursor-pointer h-full">
        <div className="relative aspect-square bg-radar-dark overflow-hidden">
          {product.image ? (
            <img 
              src={product.image} 
              alt={product.name}
              className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
              onError={(e) => {
                (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300x300/111827/00ff88?text=Sin+imagen'
              }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-500">
              <Package className="w-16 h-16" />
            </div>
          )}
          <div className="absolute top-3 right-3">
            <ScoreBadge score={score} />
          </div>
          <div className="absolute top-3 left-3 bg-radar-dark/80 backdrop-blur-sm px-2 py-1 rounded text-xs font-mono">
            {countryFlags[country?.code || 'CO'] || '🌎'} {country?.code || 'N/A'}
          </div>
          <div className="absolute bottom-3 left-3 bg-radar-accent/90 text-radar-dark px-2 py-1 rounded text-xs font-semibold capitalize">
            {product.platform}
          </div>
        </div>

        <div className="p-4 space-y-4">
          <h3 className="font-semibold text-sm line-clamp-2 leading-tight min-h-[40px]">
            {product.name}
          </h3>

          <div className="grid grid-cols-2 gap-2">
            <div className="bg-radar-dark/50 rounded-lg p-2">
              <div className="text-xs text-gray-400 mb-0.5">Ventas 7d</div>
              <div className="font-mono font-bold text-radar-accent flex items-center gap-1 text-sm">
                {product.sales7d?.toLocaleString() || 0}
                {product.sales7d > product.sales30d / 5 && <TrendingUp className="w-3 h-3" />}
              </div>
            </div>
            <div className="bg-radar-dark/50 rounded-lg p-2">
              <div className="text-xs text-gray-400 mb-0.5">Ventas 30d</div>
              <div className="font-mono font-bold text-sm">{product.sales30d?.toLocaleString() || 0}</div>
            </div>
            <div className="bg-radar-dark/50 rounded-lg p-2">
              <div className="text-xs text-gray-400 mb-0.5">Stock</div>
              <div className="font-mono font-bold text-sm">{product.stock?.toLocaleString() || 0}</div>
            </div>
            <div className="bg-radar-dark/50 rounded-lg p-2">
              <div className="text-xs text-gray-400 mb-0.5">Precio</div>
              <div className="font-mono font-bold text-sm">${(product.salePrice / 1000).toFixed(0)}k</div>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">Margen: <span className="text-radar-accent font-bold">{margin > 0 ? margin : '?'}%</span></span>
            <span className="text-gray-500 truncate max-w-[100px]">{product.supplier}</span>
          </div>
        </div>
      </div>
    </Link>
  )
}

function FilterPanel({ 
  filters, 
  setFilters, 
  isOpen, 
  onClose 
}: { 
  filters: any
  setFilters: (f: any) => void
  isOpen: boolean
  onClose: () => void
}) {
  return (
    <div className={`fixed inset-y-0 right-0 w-80 bg-radar-card border-l border-radar-border transform transition-transform duration-300 z-50 ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
      <div className="p-4 border-b border-radar-border flex items-center justify-between">
        <h3 className="font-semibold flex items-center gap-2">
          <SlidersHorizontal className="w-5 h-5 text-radar-accent" />
          Filtros
        </h3>
        <button onClick={onClose} className="p-1 hover:bg-radar-border rounded">
          <X className="w-5 h-5" />
        </button>
      </div>
      
      <div className="p-4 space-y-6 overflow-y-auto h-[calc(100vh-60px)]">
        <div>
          <label className="block text-sm font-medium mb-2">País</label>
          <select 
            value={filters.country}
            onChange={(e) => setFilters({ ...filters, country: e.target.value })}
            className="w-full bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
          >
            {DROPKILLER_COUNTRIES.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Plataforma</label>
          <select 
            value={filters.platform}
            onChange={(e) => setFilters({ ...filters, platform: e.target.value })}
            className="w-full bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
          >
            {PLATFORMS.map(p => (
              <option key={p} value={p} className="capitalize">{p}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Ventas 7 días mínimas</label>
          <input
            type="number"
            placeholder="Ej: 100"
            value={filters.s7min || ''}
            onChange={(e) => setFilters({ ...filters, s7min: e.target.value ? parseInt(e.target.value) : undefined })}
            className="w-full bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Stock mínimo</label>
          <input
            type="number"
            placeholder="Ej: 50"
            value={filters.stockMin || ''}
            onChange={(e) => setFilters({ ...filters, stockMin: e.target.value ? parseInt(e.target.value) : undefined })}
            className="w-full bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
          />
        </div>

        <div className="pt-4 border-t border-radar-border space-y-2">
          <button
            onClick={() => setFilters({ 
              country: '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
              platform: 'dropi',
              page: 1 
            })}
            className="w-full py-2 border border-radar-border rounded-lg hover:bg-radar-border transition-colors text-sm"
          >
            Limpiar filtros
          </button>
          <button
            onClick={onClose}
            className="w-full py-2 bg-radar-accent text-radar-dark rounded-lg font-semibold hover:bg-radar-accent/90 transition-colors text-sm"
          >
            Aplicar filtros
          </button>
        </div>
      </div>
    </div>
  )
}

export default function ProductosPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [usingDemo, setUsingDemo] = useState(false)
  const [filterOpen, setFilterOpen] = useState(false)
  
  const [filters, setFilters] = useState({
    country: '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
    platform: 'dropi',
    search: '',
    s7min: undefined as number | undefined,
    stockMin: undefined as number | undefined,
    page: 1,
  })

  const [searchInput, setSearchInput] = useState('')

  useEffect(() => {
    fetchProducts()
  }, [filters])

  async function fetchProducts() {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.set(key, value.toString())
        }
      })

      const response = await fetch(`/api/products?${params.toString()}`)
      
      if (!response.ok) {
        throw new Error('API no disponible')
      }
      
      const data = await response.json()
      
      if (data.products && data.products.length > 0) {
        setProducts(data.products)
        setUsingDemo(false)
      } else {
        throw new Error('Sin productos')
      }
    } catch (err) {
      console.log('Using demo data:', err)
      // Use demo data on error
      let filtered = [...DEMO_PRODUCTS]
      
      if (filters.s7min) {
        filtered = filtered.filter(p => p.sales7d >= filters.s7min!)
      }
      if (filters.stockMin) {
        filtered = filtered.filter(p => p.stock >= filters.stockMin!)
      }
      if (filters.search) {
        filtered = filtered.filter(p => 
          p.name.toLowerCase().includes(filters.search.toLowerCase())
        )
      }
      
      setProducts(filtered)
      setUsingDemo(true)
      setError(null)
    } finally {
      setLoading(false)
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setFilters({ ...filters, search: searchInput, page: 1 })
  }

  const currentCountry = DROPKILLER_COUNTRIES.find(c => c.id === filters.country)

  return (
    <div className="min-h-screen bg-radar-dark">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            🔍 Explorar <span className="gradient-text">Productos</span>
          </h1>
          <p className="text-gray-400">
            {products.length} productos {usingDemo ? '(datos demo)' : ''} en {currentCountry?.name || 'Colombia'}
          </p>
        </div>

        {usingDemo && (
          <div className="bg-radar-warning/10 border border-radar-warning/30 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-radar-warning flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-radar-warning font-medium">Modo Demo Activo</p>
              <p className="text-sm text-gray-400 mt-1">
                La API de DropKiller requiere autenticación activa. Estás viendo datos de ejemplo.
                Para datos reales, asegúrate de tener una sesión válida en DropKiller.
              </p>
            </div>
          </div>
        )}

        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <form onSubmit={handleSearch} className="flex-1 flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar productos..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-radar-card border border-radar-border rounded-lg focus:border-radar-accent focus:outline-none"
              />
            </div>
            <button 
              type="submit"
              className="px-6 py-3 bg-radar-accent text-radar-dark font-semibold rounded-lg hover:bg-radar-accent/90 transition-colors"
            >
              Buscar
            </button>
          </form>
          
          <button
            onClick={() => setFilterOpen(true)}
            className="flex items-center gap-2 px-4 py-3 bg-radar-card border border-radar-border rounded-lg hover:border-radar-accent/50 transition-colors"
          >
            <SlidersHorizontal className="w-5 h-5" />
            <span>Filtros</span>
          </button>
        </div>

        <div className="flex flex-wrap gap-2 mb-6">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-radar-accent/10 border border-radar-accent/30 rounded-full text-sm">
            <Globe className="w-4 h-4 text-radar-accent" />
            {currentCountry?.name}
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-radar-card border border-radar-border rounded-full text-sm capitalize">
            <Package className="w-4 h-4" />
            {filters.platform}
          </div>
          {filters.s7min && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-radar-card border border-radar-border rounded-full text-sm">
              <BarChart3 className="w-4 h-4" />
              Ventas 7d: ≥{filters.s7min}
            </div>
          )}
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-radar-accent animate-spin" />
            <span className="ml-3 text-gray-400">Cargando productos...</span>
          </div>
        )}

        {!loading && products.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}

        {!loading && products.length === 0 && (
          <div className="text-center py-20">
            <Package className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No se encontraron productos</h3>
            <p className="text-gray-400">Intenta ajustar los filtros o buscar algo diferente</p>
          </div>
        )}
      </main>

      <FilterPanel 
        filters={filters}
        setFilters={setFilters}
        isOpen={filterOpen}
        onClose={() => setFilterOpen(false)}
      />
      
      {filterOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setFilterOpen(false)}
        />
      )}
    </div>
  )
}
