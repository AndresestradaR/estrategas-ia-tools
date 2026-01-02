'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { 
  ArrowLeft, Play, Heart, MessageCircle, Share2, Eye,
  Loader2, ExternalLink, Download, Clock, Calendar,
  Radar, Package, Target, Zap, Users, Sparkles, 
  Volume2, Globe, Tag, TrendingUp, AlertCircle
} from 'lucide-react'

// Demo ads data
const DEMO_ADS: Record<string, any> = {
  'demo-ad-1': {
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
    images: ['https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&h=600&fit=crop'],
    videos: [],
    url: 'https://www.facebook.com/ads/library',
    creation_date: '2025-11-15',
    last_update: '2025-12-28',
    country: { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  },
  'demo-ad-2': {
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
    images: ['https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=800&h=600&fit=crop'],
    videos: [],
    url: 'https://www.facebook.com/ads/library',
    creation_date: '2025-10-01',
    last_update: '2025-12-25',
    country: { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  },
  'demo-ad-3': {
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
    images: ['https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=600&fit=crop'],
    videos: [],
    url: 'https://www.facebook.com/ads/library',
    creation_date: '2025-12-15',
    last_update: '2025-12-30',
    country: { id: '40334494-86fc-4fc0-857a-281816247906', name: 'México', code: 'MX' },
  },
  'demo-ad-4': {
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
    images: ['https://images.unsplash.com/photo-1522338242042-2d1c9cd60fc7?w=800&h=600&fit=crop'],
    videos: [],
    url: 'https://www.facebook.com/ads/library',
    creation_date: '2025-11-01',
    last_update: '2025-12-20',
    country: { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  },
  'demo-ad-5': {
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
    images: ['https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop'],
    videos: [],
    url: 'https://www.facebook.com/ads/library',
    creation_date: '2025-09-01',
    last_update: '2025-12-29',
    country: { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  },
  'demo-ad-6': {
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
    images: ['https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=800&h=600&fit=crop'],
    videos: [],
    url: 'https://www.facebook.com/ads/library',
    creation_date: '2025-11-20',
    last_update: '2025-12-27',
    country: { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  },
}

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
  url: string
  creation_date: string
  last_update: string
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

function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
}

function StatCard({ label, value, icon: Icon }: { label: string; value: string | number; icon: any }) {
  return (
    <div className="bg-radar-card border border-radar-border rounded-lg p-4 text-center">
      <Icon className="w-6 h-6 text-radar-accent mx-auto mb-2" />
      <div className="text-2xl font-bold font-mono">{value}</div>
      <div className="text-xs text-gray-400">{label}</div>
    </div>
  )
}

export default function CreativeDetailPage() {
  const params = useParams()
  const adId = params.id as string
  
  const [ad, setAd] = useState<Ad | null>(null)
  const [loading, setLoading] = useState(true)
  const [usingDemo, setUsingDemo] = useState(false)
  const [selectedMedia, setSelectedMedia] = useState<string | null>(null)
  const [isVideo, setIsVideo] = useState(false)

  useEffect(() => {
    if (adId) {
      fetchAdDetail()
    }
  }, [adId])

  async function fetchAdDetail() {
    setLoading(true)
    
    // Check if it's a demo ad first
    if (adId.startsWith('demo-ad-')) {
      const demoAd = DEMO_ADS[adId]
      if (demoAd) {
        setAd(demoAd)
        setSelectedMedia(demoAd.images?.[0] || demoAd.videos?.[0] || null)
        setIsVideo(demoAd.videos?.length > 0)
        setUsingDemo(true)
        setLoading(false)
        return
      }
    }
    
    try {
      const response = await fetch(`/api/ads/${adId}`)
      
      if (!response.ok) {
        throw new Error('API error')
      }
      
      const data = await response.json()
      const adData = data.ad || data
      
      if (adData) {
        setAd(adData)
        if (adData.videos?.length > 0) {
          setSelectedMedia(adData.videos[0])
          setIsVideo(true)
        } else if (adData.images?.length > 0) {
          setSelectedMedia(adData.images[0])
          setIsVideo(false)
        }
        setUsingDemo(false)
      } else {
        throw new Error('No ad')
      }
    } catch (err) {
      console.log('Using demo ad')
      const demoAd = DEMO_ADS[adId] || DEMO_ADS['demo-ad-1']
      setAd(demoAd)
      setSelectedMedia(demoAd.images?.[0] || null)
      setIsVideo(false)
      setUsingDemo(true)
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
          <span className="ml-3 text-gray-400">Cargando creativo...</span>
        </div>
      </div>
    )
  }

  if (!ad) {
    return (
      <div className="min-h-screen bg-radar-dark">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <Link href="/creativos" className="inline-flex items-center gap-2 text-radar-accent mb-8 hover:underline">
            <ArrowLeft className="w-5 h-5" />
            Volver a creativos
          </Link>
          <div className="bg-radar-danger/10 border border-radar-danger/30 rounded-lg p-8 text-center">
            <p className="text-radar-danger text-lg">Creativo no encontrado</p>
          </div>
        </div>
      </div>
    )
  }

  const activeDays = Math.floor(ad.active_time / (24 * 60 * 60))
  const allMedia = [...(ad.videos || []), ...(ad.images || [])]
  
  const countryFlags: Record<string, string> = {
    'CO': '🇨🇴', 'EC': '🇪🇨', 'MX': '🇲🇽', 'CL': '🇨🇱', 
    'ES': '🇪🇸', 'PE': '🇵🇪', 'PA': '🇵🇦', 'PY': '🇵🇾',
    'AR': '🇦🇷', 'GT': '🇬🇹', 'BO': '🇧🇴', 'CR': '🇨🇷'
  }

  // Demo AI analysis
  const salesAngles = [
    { angle: "Solución rápida a problema específico", description: "Enfoca en resultados inmediatos y tangibles", effectiveness_score: 92 },
    { angle: "Oferta por tiempo limitado", description: "Genera urgencia con descuentos temporales", effectiveness_score: 88 },
    { angle: "Prueba social / Testimonios", description: "Muestra clientes satisfechos y resultados reales", effectiveness_score: 85 },
    { angle: "Envío gratis / Sin riesgo", description: "Elimina objeciones de compra", effectiveness_score: 78 },
  ]

  const emotionalTriggers = [
    { trigger: "Urgencia", emotion: "FOMO", intensity: "Alta" },
    { trigger: "Confianza", emotion: "Seguridad", intensity: "Alta" },
    { trigger: "Aspiración", emotion: "Deseo de mejora", intensity: "Media" },
    { trigger: "Exclusividad", emotion: "Sentirse especial", intensity: "Media" },
  ]

  const targetDemo = {
    age_range: "25-45 años",
    gender: "65% Mujeres",
    lifestyle: ["Comprador online frecuente", "Busca ofertas", "Activo en redes sociales"],
    interests: ["E-commerce", "Belleza", "Salud", "Moda"],
    pain_points: ["Falta de tiempo", "Desconfianza en compras online", "Presupuesto limitado"]
  }

  return (
    <div className="min-h-screen bg-radar-dark">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Link href="/creativos" className="inline-flex items-center gap-2 text-radar-accent mb-8 hover:underline">
          <ArrowLeft className="w-5 h-5" />
          Volver a creativos
        </Link>

        {usingDemo && (
          <div className="bg-radar-warning/10 border border-radar-warning/30 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-radar-warning flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-radar-warning font-medium">Datos de Ejemplo</p>
              <p className="text-sm text-gray-400 mt-1">
                Este es un creativo de demostración. Los datos reales requieren conexión con Adskiller.
              </p>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Media & Basic Info */}
          <div className="space-y-6">
            <div className="relative aspect-video bg-radar-card border border-radar-border rounded-2xl overflow-hidden">
              {selectedMedia ? (
                isVideo ? (
                  <video 
                    src={selectedMedia}
                    controls
                    className="w-full h-full object-contain"
                    poster={ad.images?.[0]}
                  />
                ) : (
                  <img 
                    src={selectedMedia}
                    alt={ad.title || ad.page_name}
                    className="w-full h-full object-cover"
                  />
                )
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-500">
                  <Eye className="w-32 h-32" />
                </div>
              )}
              
              <div className="absolute top-4 left-4 bg-radar-dark/80 backdrop-blur-sm px-3 py-1.5 rounded-lg text-sm font-mono">
                {countryFlags[ad.country?.code] || '🌎'} {ad.country?.name || 'N/A'}
              </div>
              
              <div className="absolute top-4 right-4 bg-radar-accent text-radar-dark px-3 py-1.5 rounded-lg text-sm font-semibold">
                {ad.platforms?.[0] || 'Meta'}
              </div>
            </div>

            {allMedia.length > 1 && (
              <div className="flex gap-2 overflow-x-auto pb-2">
                {ad.videos?.map((video, i) => (
                  <button
                    key={`video-${i}`}
                    onClick={() => { setSelectedMedia(video); setIsVideo(true); }}
                    className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-colors relative ${
                      selectedMedia === video ? 'border-radar-accent' : 'border-radar-border hover:border-radar-accent/50'
                    }`}
                  >
                    <div className="w-full h-full bg-radar-dark flex items-center justify-center">
                      <Play className="w-6 h-6 text-white" fill="white" />
                    </div>
                  </button>
                ))}
                {ad.images?.map((image, i) => (
                  <button
                    key={`image-${i}`}
                    onClick={() => { setSelectedMedia(image); setIsVideo(false); }}
                    className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-colors ${
                      selectedMedia === image ? 'border-radar-accent' : 'border-radar-border hover:border-radar-accent/50'
                    }`}
                  >
                    <img src={image} alt="" className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            )}

            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 bg-radar-border rounded-full flex items-center justify-center text-lg font-bold">
                  {ad.page_name?.substring(0, 2).toUpperCase() || 'AD'}
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-bold">{ad.page_name || 'Página sin nombre'}</h2>
                  <p className="text-gray-400">{ad.company_name || 'Empresa'}</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-3">
              <StatCard label="Likes" value={formatNumber(ad.likes || 0)} icon={Heart} />
              <StatCard label="Comentarios" value={formatNumber(ad.comments || 0)} icon={MessageCircle} />
              <StatCard label="Compartidos" value={formatNumber(ad.shares || 0)} icon={Share2} />
              <StatCard label="Días activo" value={activeDays} icon={Clock} />
            </div>

            {(ad.title || ad.description) && (
              <div className="bg-radar-card border border-radar-border rounded-xl p-6">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Tag className="w-5 h-5 text-radar-accent" />
                  Copy del Anuncio
                </h3>
                {ad.title && <p className="font-medium mb-2">{ad.title}</p>}
                {ad.description && <p className="text-gray-400 text-sm whitespace-pre-wrap">{ad.description}</p>}
                {ad.cta && (
                  <div className="mt-4">
                    <span className="inline-block px-4 py-2 bg-radar-accent text-radar-dark rounded-lg font-semibold text-sm">
                      {ad.cta}
                    </span>
                  </div>
                )}
              </div>
            )}

            <div className="flex gap-4">
              {ad.url && (
                <a 
                  href={ad.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 flex items-center justify-center gap-2 bg-radar-accent text-radar-dark font-semibold py-3 rounded-lg hover:bg-radar-accent/90 transition-colors"
                >
                  <ExternalLink className="w-5 h-5" />
                  Ver en Meta Library
                </a>
              )}
              {selectedMedia && (
                <a 
                  href={selectedMedia}
                  download
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 flex items-center justify-center gap-2 bg-radar-card border border-radar-border py-3 rounded-lg hover:border-radar-accent/50 transition-colors"
                >
                  <Download className="w-5 h-5" />
                  Descargar
                </a>
              )}
            </div>
          </div>

          {/* Right Column - AI Analysis */}
          <div className="space-y-6">
            <div className="flex items-center gap-2 text-radar-accent">
              <Sparkles className="w-6 h-6" />
              <h2 className="text-xl font-bold">Análisis con IA</h2>
            </div>

            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="flex items-center gap-2 text-radar-accent font-semibold mb-4">
                <Target className="w-5 h-5" />
                Ángulos de Venta Detectados
              </div>
              <div className="space-y-4">
                {salesAngles.map((angle, i) => (
                  <div key={i}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-sm">{angle.angle}</span>
                      <span className="text-sm font-mono text-radar-accent">{angle.effectiveness_score}%</span>
                    </div>
                    <p className="text-xs text-gray-400 mb-2">{angle.description}</p>
                    <div className="w-full h-2 bg-radar-border rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-radar-accent rounded-full transition-all"
                        style={{ width: `${angle.effectiveness_score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="flex items-center gap-2 text-radar-accent font-semibold mb-4">
                <Zap className="w-5 h-5" />
                Triggers Emocionales
              </div>
              <div className="space-y-3">
                {emotionalTriggers.map((trigger, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-radar-dark/50 rounded-lg">
                    <div>
                      <span className="font-medium">{trigger.trigger}</span>
                      <p className="text-xs text-gray-400">{trigger.emotion}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      trigger.intensity === 'Alta' ? 'bg-radar-accent/10 text-radar-accent' :
                      trigger.intensity === 'Media' ? 'bg-radar-warning/10 text-radar-warning' :
                      'bg-gray-500/10 text-gray-400'
                    }`}>
                      {trigger.intensity}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="flex items-center gap-2 text-radar-accent font-semibold mb-4">
                <Users className="w-5 h-5" />
                Audiencia Objetivo
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-xs text-gray-400">Edad</span>
                    <p className="font-semibold">{targetDemo.age_range}</p>
                  </div>
                  <div>
                    <span className="text-xs text-gray-400">Género</span>
                    <p className="font-semibold">{targetDemo.gender}</p>
                  </div>
                </div>
                
                <div>
                  <span className="text-xs text-gray-400 mb-2 block">Intereses</span>
                  <div className="flex flex-wrap gap-2">
                    {targetDemo.interests?.map((interest, i) => (
                      <span key={i} className="px-3 py-1 bg-radar-accent/10 text-radar-accent rounded-full text-xs">
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="text-xs text-gray-400 mb-2 block">Pain Points</span>
                  <div className="flex flex-wrap gap-2">
                    {targetDemo.pain_points?.map((point, i) => (
                      <span key={i} className="px-3 py-1 bg-radar-warning/10 text-radar-warning rounded-full text-xs">
                        {point}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="flex items-center gap-2 text-gray-400 font-semibold mb-4">
                <Calendar className="w-5 h-5" />
                Información Adicional
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-xs text-gray-400">Fecha de creación</span>
                  <p>{ad.creation_date ? formatDate(ad.creation_date) : 'N/A'}</p>
                </div>
                <div>
                  <span className="text-xs text-gray-400">Última actualización</span>
                  <p>{ad.last_update ? formatDate(ad.last_update) : 'N/A'}</p>
                </div>
                <div>
                  <span className="text-xs text-gray-400">Vistas estimadas</span>
                  <p className="font-mono">{ad.views ? formatNumber(ad.views) : 'N/A'}</p>
                </div>
                <div>
                  <span className="text-xs text-gray-400">Plataformas</span>
                  <p className="capitalize">{ad.platforms?.join(', ') || 'Facebook'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
