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
  // AI Analysis
  videoAnalysis?: {
    has_watermark: boolean
    watermark_confidence: number
    language: string
  }
  productAnalysis?: {
    name: string
    brand: string
    category: string
    benefits: string[]
    claims: string[]
    target_audience: string
    price: number | null
  }
  marketingIntelligence?: {
    niche: string
    sub_niches: string[]
    value_propositions: string[]
    competitive_advantages: string[]
    price_tier: string
    visual_style: string
    narrative_approach: string
    pacing: string
    music_mood: string
    color_palette: string[]
    engagement_drivers: string[]
  }
  keywords?: Array<{
    keyword: string
    frequency: number
    relevance_score: number
  }>
  salesAngles?: Array<{
    angle: string
    description: string
    effectiveness_score: number
  }>
  emotionalTriggers?: Array<{
    trigger: string
    emotion: string
    intensity: string
  }>
  targetDemographics?: Array<{
    age_range: string
    gender: string
    lifestyle: string[]
    interests: string[]
    pain_points: string[]
  }>
  conversionTactics?: Array<{
    tactic: string
    description: string
    urgency_level: string
  }>
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
  const [error, setError] = useState<string | null>(null)
  const [selectedMedia, setSelectedMedia] = useState<string | null>(null)
  const [isVideo, setIsVideo] = useState(false)

  useEffect(() => {
    if (adId) {
      fetchAdDetail()
    }
  }, [adId])

  async function fetchAdDetail() {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`/api/ads/${adId}`)
      
      if (!response.ok) {
        throw new Error('Error al cargar el creativo')
      }
      
      const data = await response.json()
      setAd(data.ad || data)
      
      // Set initial media
      if (data.ad?.videos?.length > 0 || data.videos?.length > 0) {
        setSelectedMedia((data.ad?.videos || data.videos)[0])
        setIsVideo(true)
      } else if (data.ad?.images?.length > 0 || data.images?.length > 0) {
        setSelectedMedia((data.ad?.images || data.images)[0])
        setIsVideo(false)
      }
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
          <span className="ml-3 text-gray-400">Cargando creativo...</span>
        </div>
      </div>
    )
  }

  if (error || !ad) {
    return (
      <div className="min-h-screen bg-radar-dark">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <Link href="/creativos" className="inline-flex items-center gap-2 text-radar-accent mb-8 hover:underline">
            <ArrowLeft className="w-5 h-5" />
            Volver a creativos
          </Link>
          <div className="bg-radar-danger/10 border border-radar-danger/30 rounded-lg p-8 text-center">
            <p className="text-radar-danger text-lg">{error || 'Creativo no encontrado'}</p>
            <button 
              onClick={fetchAdDetail}
              className="mt-4 text-sm underline hover:no-underline"
            >
              Reintentar
            </button>
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
    'AR': '🇦🇷', 'GT': '🇬🇹', 'BO': '🇧🇴', 'CR': '🇨🇷',
    'UY': '🇺🇾', 'VE': '🇻🇪'
  }

  // Generate demo AI analysis if not present
  const salesAngles = ad.salesAngles || [
    { angle: "Solución rápida", description: "Enfoca en resultados inmediatos", effectiveness_score: 85 },
    { angle: "Precio especial", description: "Oferta por tiempo limitado", effectiveness_score: 78 },
    { angle: "Testimonios", description: "Prueba social de clientes", effectiveness_score: 72 },
  ]

  const emotionalTriggers = ad.emotionalTriggers || [
    { trigger: "Urgencia", emotion: "FOMO", intensity: "Alta" },
    { trigger: "Confianza", emotion: "Seguridad", intensity: "Media" },
    { trigger: "Aspiración", emotion: "Deseo", intensity: "Alta" },
  ]

  const targetDemo = ad.targetDemographics?.[0] || {
    age_range: "25-45",
    gender: "Unisex",
    lifestyle: ["Comprador online", "Busca ofertas"],
    interests: ["E-commerce", "Ofertas", "Productos nuevos"],
    pain_points: ["Falta de tiempo", "Desconfianza en compras online"]
  }

  return (
    <div className="min-h-screen bg-radar-dark">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Back Button */}
        <Link href="/creativos" className="inline-flex items-center gap-2 text-radar-accent mb-8 hover:underline">
          <ArrowLeft className="w-5 h-5" />
          Volver a creativos
        </Link>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Media & Basic Info */}
          <div className="space-y-6">
            {/* Main Media */}
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
                    className="w-full h-full object-contain"
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

            {/* Media Thumbnails */}
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
                    <img src={ad.images?.[0] || ''} alt="" className="w-full h-full object-cover" />
                    <div className="absolute inset-0 flex items-center justify-center bg-black/40">
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

            {/* Page Info */}
            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 bg-radar-border rounded-full flex items-center justify-center text-lg font-bold">
                  {ad.page_name?.substring(0, 2).toUpperCase() || 'AD'}
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-bold">{ad.page_name || 'Página sin nombre'}</h2>
                  <p className="text-gray-400">{ad.company_name || 'Empresa'}</p>
                  {ad.link && (
                    <a 
                      href={ad.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-radar-accent hover:underline flex items-center gap-1 mt-1"
                    >
                      {ad.link.substring(0, 40)}...
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            </div>

            {/* Engagement Stats */}
            <div className="grid grid-cols-4 gap-3">
              <StatCard label="Likes" value={formatNumber(ad.likes || 0)} icon={Heart} />
              <StatCard label="Comentarios" value={formatNumber(ad.comments || 0)} icon={MessageCircle} />
              <StatCard label="Compartidos" value={formatNumber(ad.shares || 0)} icon={Share2} />
              <StatCard label="Días activo" value={activeDays} icon={Clock} />
            </div>

            {/* Ad Copy */}
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

            {/* Action Buttons */}
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

            {/* Sales Angles */}
            <div className="bg-radar-card border border-radar-border rounded-xl p-6">
              <div className="flex items-center gap-2 text-radar-accent font-semibold mb-4">
                <Target className="w-5 h-5" />
                Ángulos de Venta
              </div>
              <div className="space-y-4">
                {salesAngles.map((angle, i) => (
                  <div key={i}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium">{angle.angle}</span>
                      <span className="text-sm font-mono text-radar-accent">{angle.effectiveness_score}%</span>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">{angle.description}</p>
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

            {/* Emotional Triggers */}
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

            {/* Target Demographics */}
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

            {/* Video Analysis */}
            {ad.videoAnalysis && (
              <div className="bg-radar-card border border-radar-border rounded-xl p-6">
                <div className="flex items-center gap-2 text-radar-accent font-semibold mb-4">
                  <Volume2 className="w-5 h-5" />
                  Análisis de Video
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-xs text-gray-400">Idioma</span>
                    <p className="font-semibold capitalize">{ad.videoAnalysis.language || 'Español'}</p>
                  </div>
                  <div>
                    <span className="text-xs text-gray-400">Marca de agua</span>
                    <p className={`font-semibold ${ad.videoAnalysis.has_watermark ? 'text-radar-warning' : 'text-radar-accent'}`}>
                      {ad.videoAnalysis.has_watermark ? 'Sí detectada' : 'No detectada'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Marketing Intelligence */}
            {ad.marketingIntelligence && (
              <div className="bg-radar-card border border-radar-border rounded-xl p-6">
                <div className="flex items-center gap-2 text-radar-accent font-semibold mb-4">
                  <TrendingUp className="w-5 h-5" />
                  Inteligencia de Marketing
                </div>
                <div className="space-y-3">
                  {ad.marketingIntelligence.niche && (
                    <div>
                      <span className="text-xs text-gray-400">Nicho</span>
                      <p className="font-semibold">{ad.marketingIntelligence.niche}</p>
                    </div>
                  )}
                  {ad.marketingIntelligence.value_propositions?.length > 0 && (
                    <div>
                      <span className="text-xs text-gray-400 mb-2 block">Propuestas de valor</span>
                      <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
                        {ad.marketingIntelligence.value_propositions.map((prop, i) => (
                          <li key={i}>{prop}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {ad.marketingIntelligence.color_palette?.length > 0 && (
                    <div>
                      <span className="text-xs text-gray-400 mb-2 block">Paleta de colores</span>
                      <div className="flex gap-2">
                        {ad.marketingIntelligence.color_palette.map((color, i) => (
                          <div 
                            key={i}
                            className="w-8 h-8 rounded-full border border-radar-border"
                            style={{ backgroundColor: color }}
                            title={color}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Metadata */}
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
                  <span className="text-xs text-gray-400">ID Creativo</span>
                  <p className="font-mono text-xs">{ad.creative_id || ad.id}</p>
                </div>
                <div>
                  <span className="text-xs text-gray-400">Plataforma</span>
                  <p>{ad.platforms?.join(', ') || 'Facebook'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
