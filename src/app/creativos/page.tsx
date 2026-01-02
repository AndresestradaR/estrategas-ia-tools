'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { 
  Search, Play, Heart, MessageCircle, Share2, Eye,
  ChevronLeft, ChevronRight, Loader2, X, SlidersHorizontal,
  Radar, Package, Globe, Clock, Sparkles, AlertCircle
} from 'lucide-react'

const ADSKILLER_COUNTRIES = [
  { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  { id: '40334494-86fc-4fc0-857a-281816247906', name: 'México', code: 'MX' },
  { id: '1be5939b-f5b1-41ea-8546-fc72a7381c9d', name: 'Ecuador', code: 'EC' },
  { id: '8e7e6e88-2a90-4a8d-b6eb-ed0975c1df59', name: 'Perú', code: 'PE' },
  { id: 'bed193de-9cda-47b7-ab21-fc4abde86bd1', name: 'Chile', code: 'CL' },
  { id: 'e8a05443-3d9c-4a24-93f0-1d197923d1fe', name: 'Argentina', code: 'AR' },
  { id: 'de1f3f37-ed5f-4335-b151-974932bcbd83', name: 'Bolivia', code: 'BO' },
  { id: '3a44b739-d1c1-4fc5-8742-ae691d09c434', name: 'Costa Rica', code: 'CR' },
  { id: '2361e5ee-f992-476c-a380-2a157e384a60', name: 'España', code: 'ES' },
]

const DEMO_ADS = [
  {
    id: 'demo-ad-1',
    page_name: 'Beauty Store CO',
    company_name: 'Beauty Imports SAS',
    title: '✨ El sérum que está revolucionando el cuidado de la piel en Colombia',
    description: '🔥 OFERTA ESPECIAL: 50% OFF solo por hoy\n\n✅ Vitamina C pura\n✅ Resultados en 7 días\n✅ Envío gratis\n\n👇 Haz clic en "Comprar ahora"',
    likes: 12500,
    comments: 890,
    shares: 2340,
    views: 458000,
    active_time: 1209600,
    cta: 'Comprar ahora',
    platforms: ['facebook', 'instagram'],
    images: ['https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&h=400&fit=crop'],
    videos: [],
    country: { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  },
  {
    id: 'demo-ad-2',
    page_name: 'FajasColombia',
    company_name: 'Moda Latina',
    title: '👙 La faja #1 en ventas que moldea tu figura al instante',
    description: '💪 Reduce hasta 3 tallas\n🎯 Postparto y uso diario\n📦 Envío discreto\n\n¡Miles de mujeres ya la tienen!',
    likes: 8900,
    comments: 1250,
    shares: 3100,
    views: 320000,
    active_time: 2592000,
    cta: 'Ver más',
    platforms: ['facebook'],
    images: ['https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600&h=400&fit=crop'],
    videos: [],
    country: { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  },
  {
    id: 'demo-ad-3',
    page_name: 'TechGadgets MX',
    company_name: 'Importaciones Tech',
    title: '🎧 Audífonos Bluetooth que los influencers no quieren que conozcas',
    description: '⚡ 40 horas de batería\n🔊 Sonido HD\n💧 Resistente al agua\n\n🔥 Precio especial de lanzamiento',
    likes: 15600,
    comments: 2100,
    shares: 4500,
    views: 890000,
    active_time: 604800,
    cta: 'Comprar',
    platforms: ['facebook', 'instagram'],
    images: ['https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop'],
    videos: [],
    country: { id: '40334494-86fc-4fc0-857a-281816247906', name: 'México', code: 'MX' },
  },
  {
    id: 'demo-ad-4',
    page_name: 'Belleza Express',
    company_name: 'Beauty Tools CO',
    title: '💇‍♀️ Plancha profesional con tecnología de salón',
    description: '✨ Cerámica tourmalina\n🌡️ Control de temperatura\n⚡ Calienta en 30 segundos\n\n👩‍🦰 Perfecta para todo tipo de cabello',
    likes: 6700,
    comments: 450,
    shares: 1200,
    views: 210000,
    active_time: 1814400,
    cta: 'Obtener oferta',
    platforms: ['instagram'],
    images: ['https://images.unsplash.com/photo-1522338242042-2d1c9cd60fc7?w=600&h=400&fit=crop'],
    videos: [],
    country: { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  },
  {
    id: 'demo-ad-5',
    page_name: 'Salud y Bienestar',
    company_name: 'Health Plus SAS',
    title: '🧘 Corrector de postura que alivia el dolor de espalda',
    description: '✅ Usado por fisioterapeutas\n✅ Resultados desde el día 1\n✅ Discreto bajo la ropa\n\n🎁 ENVÍO GRATIS hoy',
    likes: 23400,
    comments: 3200,
    shares: 8900,
    views: 1250000,
    active_time: 3456000,
    cta: 'Comprar ahora',
    platforms: ['facebook', 'instagram'],
    images: ['https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=400&fit=crop'],
    videos: [],
    country: { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  },
  {
    id: 'demo-ad-6',
    page_name: 'Makeup Paradise',
    company_name: 'Cosméticos Express',
    title: '💄 Kit de maquillaje profesional - 24 piezas',
    description: '🎨 Todo lo que necesitas en un solo kit\n💰 Ahorra más de $200.000\n📦 Estuche premium incluido\n\n⏰ Últimas unidades',
    likes: 9800,
    comments: 780,
    shares: 2100,
    views: 380000,
    active_time: 1296000,
    cta: 'Ver más',
    platforms: ['facebook'],
    images: ['https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&h=400&fit=crop'],
    videos: [],
    country: { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  },
]

interface Ad {
  id: string
  page_name: string
  company_name: string
  title: string
  description: string
  likes: number
  comments: number
  shares: number
  views: number | null
  active_time: number
  cta: string
  platforms: string[]
  images: string[]
  videos: string[]
  country: { id: string; name: string; code: string }
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

function AdCard({ ad }: { ad: Ad }) {
  const thumbnail = ad.images?.[0] || ad.videos?.[0] || ''
  const hasVideo = ad.videos && ad.videos.length > 0
  const activeDays = Math.floor(ad.active_time / (24 * 60 * 60))
  
  const countryFlags: Record<string, string> = {
    'CO': '🇨🇴', 'EC': '🇪🇨', 'MX': '🇲🇽', 'CL': '🇨🇱', 
    'ES': '🇪🇸', 'PE': '🇵🇪', 'PA': '🇵🇦', 'PY': '🇵🇾',
    'AR': '🇦🇷', 'GT': '🇬🇹', 'BO': '🇧🇴', 'CR': '🇨🇷'
  }

  return (
    <Link href={`/creativos/${ad.id}`}>
      <div className="bg-radar-card border border-radar-border rounded-xl overflow-hidden transition-all duration-300 hover:border-radar-accent/50 hover:shadow-lg hover:shadow-radar-accent/10 cursor-pointer h-full">
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

        <div className="p-4 space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-radar-border rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">
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
  const [usingDemo, setUsingDemo] = useState(false)
  const [filterOpen, setFilterOpen] = useState(false)
  
  const [filters, setFilters] = useState({
    countryId: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47',
    platform: 'facebook',
    search: '',
    sortBy: 'updated_at',
    page: 1,
  })

  const [searchInput, setSearchInput] = useState('')

  useEffect(() => {
    fetchAds()
  }, [filters])

  async function fetchAds() {
    setLoading(true)
    
    try {
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.set(key, value.toString())
        }
      })

      const response = await fetch(`/api/ads?${params.toString()}`)
      
      if (!response.ok) {
        throw new Error('API no disponible')
      }
      
      const data = await response.json()
      
      if (data.ads && data.ads.length > 0) {
        setAds(data.ads)
        setUsingDemo(false)
      } else {
        throw new Error('Sin creativos')
      }
    } catch (err) {
      console.log('Using demo ads:', err)
      let filtered = [...DEMO_ADS]
      
      if (filters.search) {
        filtered = filtered.filter(a => 
          a.title.toLowerCase().includes(filters.search.toLowerCase()) ||
          a.page_name.toLowerCase().includes(filters.search.toLowerCase())
        )
      }
      
      if (filters.sortBy === 'likes') {
        filtered.sort((a, b) => b.likes - a.likes)
      } else if (filters.sortBy === 'comments') {
        filtered.sort((a, b) => b.comments - a.comments)
      } else if (filters.sortBy === 'shares') {
        filtered.sort((a, b) => b.shares - a.shares)
      }
      
      setAds(filtered)
      setUsingDemo(true)
    } finally {
      setLoading(false)
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    setFilters({ ...filters, search: searchInput, page: 1 })
  }

  const currentCountry = ADSKILLER_COUNTRIES.find(c => c.id === filters.countryId)

  return (
    <div className="min-h-screen bg-radar-dark">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            🎬 Explorar <span className="gradient-text">Creativos</span>
          </h1>
          <p className="text-gray-400">
            {ads.length} anuncios {usingDemo ? '(datos demo)' : ''} en {currentCountry?.name || 'Colombia'}
          </p>
        </div>

        {usingDemo && (
          <div className="bg-radar-warning/10 border border-radar-warning/30 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-radar-warning flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-radar-warning font-medium">Modo Demo Activo</p>
              <p className="text-sm text-gray-400 mt-1">
                La API de Adskiller requiere autenticación activa. Estás viendo datos de ejemplo.
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

        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-radar-accent animate-spin" />
            <span className="ml-3 text-gray-400">Cargando creativos...</span>
          </div>
        )}

        {!loading && ads.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {ads.map((ad) => (
              <AdCard key={ad.id} ad={ad} />
            ))}
          </div>
        )}

        {!loading && ads.length === 0 && (
          <div className="text-center py-20">
            <Eye className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No se encontraron creativos</h3>
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
