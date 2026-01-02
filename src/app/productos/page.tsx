'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { 
  Search, Filter, TrendingUp, Package, DollarSign, 
  ChevronLeft, ChevronRight, Loader2, X, SlidersHorizontal,
  Radar, Eye, Zap, Globe, BarChart3
} from 'lucide-react'
import { DROPKILLER_COUNTRIES, PLATFORMS } from '@/types'

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
}

interface ProductsResponse {
  products: Product[]
  total: number
  page: number
  limit: number
  totalPages: number
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
  // Score basado en ventas, stock y tendencia
  let score = 5
  
  // Ventas 7d
  if (product.sales7d > 500) score += 2
  else if (product.sales7d > 200) score += 1.5
  else if (product.sales7d > 100) score += 1
  else if (product.sales7d > 50) score += 0.5
  
  // Ratio ventas 7d vs 30d (tendencia)
  const weeklyRatio = product.sales30d > 0 ? (product.sales7d * 4) / product.sales30d : 0
  if (weeklyRatio > 1.5) score += 1.5 // Trending up
  else if (weeklyRatio > 1.2) score += 1
  else if (weeklyRatio < 0.7) score -= 1 // Trending down
  
  // Stock saludable
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
        {/* Image */}
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

        {/* Content */}
        <div className="p-4 space-y-4">
          <h3 className="font-semibold text-sm line-clamp-2 leading-tight min-h-[40px]">
            {product.name}
          </h3>

          {/* Stats Grid */}
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

          {/* Margin & Supplier */}
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
        {/* País */}
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

        {/* Plataforma */}
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

        {/* Ventas 7d */}
        <div>
          <label className="block text-sm font-medium mb-2">Ventas 7 días</label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              placeholder="Mín"
              value={filters.s7min || ''}
              onChange={(e) => setFilters({ ...filters, s7min: e.target.value ? parseInt(e.target.value) : undefined })}
              className="bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
            />
            <input
              type="number"
              placeholder="Máx"
              value={filters.s7max || ''}
              onChange={(e) => setFilters({ ...filters, s7max: e.target.value ? parseInt(e.target.value) : undefined })}
              className="bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
            />
          </div>
        </div>

        {/* Ventas 30d */}
        <div>
          <label className="block text-sm font-medium mb-2">Ventas 30 días</label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              placeholder="Mín"
              value={filters.s30min || ''}
              onChange={(e) => setFilters({ ...filters, s30min: e.target.value ? parseInt(e.target.value) : undefined })}
              className="bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
            />
            <input
              type="number"
              placeholder="Máx"
              value={filters.s30max || ''}
              onChange={(e) => setFilters({ ...filters, s30max: e.target.value ? parseInt(e.target.value) : undefined })}
              className="bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
            />
          </div>
        </div>

        {/* Stock */}
        <div>
          <label className="block text-sm font-medium mb-2">Stock</label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              placeholder="Mín"
              value={filters.stockMin || ''}
              onChange={(e) => setFilters({ ...filters, stockMin: e.target.value ? parseInt(e.target.value) : undefined })}
              className="bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
            />
            <input
              type="number"
              placeholder="Máx"
              value={filters.stockMax || ''}
              onChange={(e) => setFilters({ ...filters, stockMax: e.target.value ? parseInt(e.target.value) : undefined })}
              className="bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
            />
          </div>
        </div>

        {/* Precio */}
        <div>
          <label className="block text-sm font-medium mb-2">Precio de venta</label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              placeholder="Mín"
              value={filters.priceMin || ''}
              onChange={(e) => setFilters({ ...filters, priceMin: e.target.value ? parseInt(e.target.value) : undefined })}
              className="bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
            />
            <input
              type="number"
              placeholder="Máx"
              value={filters.priceMax || ''}
              onChange={(e) => setFilters({ ...filters, priceMax: e.target.value ? parseInt(e.target.value) : undefined })}
              className="bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
            />
          </div>
        </div>

        {/* Clear & Apply */}
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
  const router = useRouter()
  const searchParams = useSearchParams()
  
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [filterOpen, setFilterOpen] = useState(false)
  
  const [filters, setFilters] = useState({
    country: searchParams.get('country') || '65c75a5f-0c4a-45fb-8c90-5b538805a15a',
    platform: searchParams.get('platform') || 'dropi',
    search: searchParams.get('search') || '',
    s7min: searchParams.get('s7min') ? parseInt(searchParams.get('s7min')!) : undefined,
    s7max: searchParams.get('s7max') ? parseInt(searchParams.get('s7max')!) : undefined,
    s30min: searchParams.get('s30min') ? parseInt(searchParams.get('s30min')!) : undefined,
    s30max: searchParams.get('s30max') ? parseInt(searchParams.get('s30max')!) : undefined,
    stockMin: searchParams.get('stockMin') ? parseInt(searchParams.get('stockMin')!) : undefined,
    stockMax: searchParams.get('stockMax') ? parseInt(searchParams.get('stockMax')!) : undefined,
    priceMin: searchParams.get('priceMin') ? parseInt(searchParams.get('priceMin')!) : undefined,
    priceMax: searchParams.get('priceMax') ? parseInt(searchParams.get('priceMax')!) : undefined,
    page: searchParams.get('page') ? parseInt(searchParams.get('page')!) : 1,
  })

  const [searchInput, setSearchInput] = useState(filters.search)

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
        throw new Error('Error al cargar productos')
      }
      
      const data: ProductsResponse = await response.json()
      setProducts(data.products || [])
      setTotalPages(data.totalPages || 1)
      setTotal(data.total || 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
      setProducts([])
    } finally {
      setLoading(false)
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setFilters({ ...filters, search: searchInput, page: 1 })
  }

  function handlePageChange(newPage: number) {
    setFilters({ ...filters, page: newPage })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const currentCountry = DROPKILLER_COUNTRIES.find(c => c.id === filters.country)

  return (
    <div className="min-h-screen bg-radar-dark">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Title & Stats */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            🔍 Explorar <span className="gradient-text">Productos</span>
          </h1>
          <p className="text-gray-400">
            {total.toLocaleString()} productos encontrados en {currentCountry?.name || 'todos los países'}
          </p>
        </div>

        {/* Search & Filters Bar */}
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

        {/* Quick Filters */}
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

        {/* Error State */}
        {error && (
          <div className="bg-radar-danger/10 border border-radar-danger/30 rounded-lg p-4 mb-8">
            <p className="text-radar-danger">{error}</p>
            <button 
              onClick={fetchProducts}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Reintentar
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-radar-accent animate-spin" />
            <span className="ml-3 text-gray-400">Cargando productos...</span>
          </div>
        )}

        {/* Products Grid */}
        {!loading && products.length > 0 && (
          <>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-center gap-4 mt-8">
              <button
                onClick={() => handlePageChange(filters.page - 1)}
                disabled={filters.page <= 1}
                className="flex items-center gap-2 px-4 py-2 bg-radar-card border border-radar-border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:border-radar-accent/50 transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
                Anterior
              </button>
              
              <span className="text-gray-400">
                Página {filters.page} de {totalPages}
              </span>
              
              <button
                onClick={() => handlePageChange(filters.page + 1)}
                disabled={filters.page >= totalPages}
                className="flex items-center gap-2 px-4 py-2 bg-radar-card border border-radar-border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:border-radar-accent/50 transition-colors"
              >
                Siguiente
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </>
        )}

        {/* Empty State */}
        {!loading && products.length === 0 && !error && (
          <div className="text-center py-20">
            <Package className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No se encontraron productos</h3>
            <p className="text-gray-400">Intenta ajustar los filtros o buscar algo diferente</p>
          </div>
        )}
      </main>

      {/* Filter Panel */}
      <FilterPanel 
        filters={filters}
        setFilters={setFilters}
        isOpen={filterOpen}
        onClose={() => setFilterOpen(false)}
      />
      
      {/* Overlay */}
      {filterOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setFilterOpen(false)}
        />
      )}
    </div>
  )
}
