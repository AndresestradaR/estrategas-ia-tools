'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  Search, Filter, Play, Heart, MessageCircle, Share2, Eye,
  ChevronLeft, ChevronRight, Loader2, X, SlidersHorizontal,
  Radar, Package, Globe, Clock, ExternalLink, Download, Sparkles
} from 'lucide-react'
import { ADSKILLER_COUNTRIES } from '@/types'

interface Ad {
  id: string
  external_ad_id: string
  creation_date: string
  start_date: string
  end_date: string
  last_update: string
  platforms: string[]
  page_name: string
  company_name: string
  likes: number
  comments: number
  shares: number
  views: number | null
  active_time: number
  title: string
  description: string
  link: string
  cta: string
  videos: string[]
  images: string[]
  url: string
  page_id: string
  creative_id: string
  country_id: string
  enabled: boolean
  country: {
    id: string
    name: string
    code: string
  }
}

interface AdsResponse {
  ads: Ad[]
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
            <Link href="/productos" className="text-gray-400 hover:text-radar-accent transition-colors flex items-center gap-2">
              <Package className="w-4 h-4" />
              Productos
            </Link>
            <Link href="/creativos" className="text-radar-accent font-medium flex items-center gap-2">
              <Eye className="w-4 h-4" />
              Creativos
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}

function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

function AdCard({ ad }: { ad: Ad }) {
  const thumbnail = ad.images?.[0] || ad.videos?.[0] || ''
  const hasVideo = ad.videos && ad.videos.length > 0
  const activeDays = Math.floor(ad.active_time / (24 * 60 * 60))
  
  const countryFlags: Record<string, string> = {
    'CO': '🇨🇴', 'EC': '🇪🇨', 'MX': '🇲🇽', 'CL': '🇨🇱', 
    'ES': '🇪🇸', 'PE': '🇵🇪', 'PA': '🇵🇦', 'PY': '🇵🇾',
    'AR': '🇦🇷', 'GT': '🇬🇹', 'BO': '🇧🇴', 'CR': '🇨🇷',
    'UY': '🇺🇾', 'VE': '🇻🇪'
  }

  return (
    <Link href={`/creativos/${ad.id}`}>
      <div className="bg-radar-card border border-radar-border rounded-xl overflow-hidden transition-all duration-300 hover:border-radar-accent/50 hover:shadow-lg hover:shadow-radar-accent/10 cursor-pointer h-full">
        {/* Thumbnail */}
        <div className="relative aspect-video bg-radar-dark overflow-hidden">
          {thumbnail ? (
            <img 
              src={thumbnail} 
              alt={ad.title || ad.page_name}
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x225/111827/00ff88?text=Sin+preview'
              }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-500">
              <Eye className="w-16 h-16" />
            </div>
          )}
          
          {hasVideo && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/30">
              <div className="w-14 h-14 bg-radar-accent/90 rounded-full flex items-center justify-center">
                <Play className="w-6 h-6 text-radar-dark ml-1" fill="currentColor" />
              </div>
            </div>
          )}
          
          <div className="absolute top-3 left-3 bg-radar-dark/80 backdrop-blur-sm px-2 py-1 rounded text-xs font-mono">
            {countryFlags[ad.country?.code] || '🌎'} {ad.country?.code || 'N/A'}
          </div>
          
          <div className="absolute top-3 right-3 bg-radar-accent/90 text-radar-dark px-2 py-1 rounded text-xs font-semibold">
            {ad.platforms?.[0] || 'Meta'}
          </div>
          
          {activeDays > 0 && (
            <div className="absolute bottom-3 right-3 bg-radar-dark/80 backdrop-blur-sm px-2 py-1 rounded text-xs flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {activeDays}d activo
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4 space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-radar-border rounded-full flex items-center justify-center text-xs font-bold">
              {ad.page_name?.substring(0, 2).toUpperCase() || 'AD'}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-sm line-clamp-1">{ad.page_name || 'Sin nombre'}</h3>
              <p className="text-xs text-gray-400 line-clamp-1">{ad.company_name || 'Empresa'}</p>
            </div>
          </div>

          {ad.title && (
            <p className="text-sm text-gray-300 line-clamp-2">{ad.title}</p>
          )}

          {/* Engagement Stats */}
          <div className="flex items-center gap-4 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Heart className="w-3.5 h-3.5" />
              {formatNumber(ad.likes || 0)}
            </span>
            <span className="flex items-center gap-1">
              <MessageCircle className="w-3.5 h-3.5" />
              {formatNumber(ad.comments || 0)}
            </span>
            <span className="flex items-center gap-1">
              <Share2 className="w-3.5 h-3.5" />
              {formatNumber(ad.shares || 0)}
            </span>
            {ad.views && (
              <span className="flex items-center gap-1">
                <Eye className="w-3.5 h-3.5" />
                {formatNumber(ad.views)}
              </span>
            )}
          </div>

          {/* CTA */}
          {ad.cta && (
            <div className="pt-2 border-t border-radar-border">
              <span className="inline-block px-3 py-1 bg-radar-dark text-xs rounded-full">
                {ad.cta}
              </span>
            </div>
          )}
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
            value={filters.countryId}
            onChange={(e) => setFilters({ ...filters, countryId: e.target.value })}
            className="w-full bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
          >
            {ADSKILLER_COUNTRIES.map(c => (
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
            <option value="facebook">Facebook / Instagram</option>
            <option value="tiktok">TikTok</option>
          </select>
        </div>

        {/* Ordenar */}
        <div>
          <label className="block text-sm font-medium mb-2">Ordenar por</label>
          <select 
            value={filters.sortBy}
            onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
            className="w-full bg-radar-dark border border-radar-border rounded-lg p-2 text-sm"
          >
            <option value="updated_at">Más recientes</option>
            <option value="likes">Más likes</option>
            <option value="comments">Más comentarios</option>
            <option value="shares">Más compartidos</option>
            <option value="active_time">Tiempo activo</option>
          </select>
        </div>

        {/* Clear & Apply */}
        <div className="pt-4 border-t border-radar-border space-y-2">
          <button
            onClick={() => setFilters({ 
              countryId: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47',
              platform: 'facebook',
              sortBy: 'updated_at',
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

export default function CreativosPage() {
  const [ads, setAds] = useState<Ad[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [filterOpen, setFilterOpen] = useState(false)
  
  const [filters, setFilters] = useState({
    countryId: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', // Colombia
    platform: 'facebook',
    search: '',
    sortBy: 'updated_at',
    order: 'desc' as const,
    page: 1,
  })

  const [searchInput, setSearchInput] = useState(filters.search)

  useEffect(() => {
    fetchAds()
  }, [filters])

  async function fetchAds() {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.set(key, value.toString())
        }
      })

      const response = await fetch(`/api/ads?${params.toString()}`)
      
      if (!response.ok) {
        throw new Error('Error al cargar creativos')
      }
      
      const data: AdsResponse = await response.json()
      setAds(data.ads || [])
      setTotalPages(data.totalPages || 1)
      setTotal(data.total || 0)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido')
      setAds([])
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

  const currentCountry = ADSKILLER_COUNTRIES.find(c => c.id === filters.countryId)

  return (
    <div className="min-h-screen bg-radar-dark">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Title & Stats */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            🎬 Explorar <span className="gradient-text">Creativos</span>
          </h1>
          <p className="text-gray-400">
            {total.toLocaleString()} anuncios encontrados en {currentCountry?.name || 'todos los países'}
          </p>
        </div>

        {/* Search & Filters Bar */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <form onSubmit={handleSearch} className="flex-1 flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por página o contenido..."
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
            <Play className="w-4 h-4" />
            {filters.platform === 'facebook' ? 'Meta Ads' : 'TikTok Ads'}
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-radar-card border border-radar-border rounded-full text-sm">
            <Sparkles className="w-4 h-4" />
            Con análisis IA
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-radar-danger/10 border border-radar-danger/30 rounded-lg p-4 mb-8">
            <p className="text-radar-danger">{error}</p>
            <button 
              onClick={fetchAds}
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
            <span className="ml-3 text-gray-400">Cargando creativos...</span>
          </div>
        )}

        {/* Ads Grid */}
        {!loading && ads.length > 0 && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {ads.map((ad) => (
                <AdCard key={ad.id} ad={ad} />
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
        {!loading && ads.length === 0 && !error && (
          <div className="text-center py-20">
            <Eye className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No se encontraron creativos</h3>
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
