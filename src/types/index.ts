// Tipos para DropKiller Products API
export interface DropKillerProduct {
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
  // Métricas
  sales7d: number
  sales30d: number
  billing7d: number
  billing30d: number
  // Historial
  history?: ProductHistory[]
}

export interface ProductHistory {
  date: string
  stock: number
  billing: number
  salePrice: number
  soldUnits: number
  stockAdjustment: boolean
  stockAdjustmentReason: string | null
}

// Tipos para Adskiller API
export interface AdskillerAd {
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
  // Análisis IA
  videoAnalysis?: VideoAnalysis
  productAnalysis?: ProductAnalysis
  marketingIntelligence?: MarketingIntelligence
  keywords?: Keyword[]
  salesAngles?: SalesAngle[]
  emotionalTriggers?: EmotionalTrigger[]
  targetDemographics?: TargetDemographic[]
  conversionTactics?: ConversionTactic[]
  onScreenText?: OnScreenText[]
}

export interface VideoAnalysis {
  id: string
  ad_id: string
  has_watermark: boolean
  watermark_confidence: number
  watermark_description: string
  language: string
  embedding_text: string
  analysis_timestamp: string
}

export interface ProductAnalysis {
  id: string
  video_analysis_id: string
  name: string
  brand: string
  category: string
  variants: string[]
  benefits: string[]
  claims: string[]
  results: string[]
  packaging_type: string
  packaging_material: string
  color_variants: string[]
  materials: string[]
  how_to: string[]
  applications: string[]
  target_audience: string
  need_state: string
  tone: string
  target_language: string
  logos: string[]
  price: number | null
  discount: number | null
}

export interface MarketingIntelligence {
  id: string
  video_analysis_id: string
  niche: string
  sub_niches: string[]
  value_propositions: string[]
  competitive_advantages: string[]
  price_tier: string
  brand_personality: string
  market_segment: string
  differentiation_strategy: string
  visual_style: string
  narrative_approach: string
  pacing: string
  music_mood: string
  color_palette: string[]
  engagement_drivers: string[]
  conversion_signals: string[]
  retention_factors: string[]
}

export interface Keyword {
  id: string
  marketing_intelligence_id: string
  keyword: string
  frequency: number
  context: string
  relevance_score: number
}

export interface SalesAngle {
  id: string
  marketing_intelligence_id: string
  angle: string
  description: string
  effectiveness_score: number
}

export interface EmotionalTrigger {
  id: string
  trigger: string
  emotion: string
  intensity: string
}

export interface TargetDemographic {
  id: string
  age_range: string
  gender: string
  income_level: string
  lifestyle: string[]
  interests: string[]
  pain_points: string[]
}

export interface ConversionTactic {
  id: string
  tactic: string
  description: string
  urgency_level: string
}

export interface OnScreenText {
  id: string
  product_analysis_id: string
  text: string
  t_start_s: number
  t_end_s: number
  x: number
  y: number
  width: number
  height: number
}

// Tipos para filtros
export interface ProductFilters {
  platform?: string
  country?: string
  s7min?: number
  s7max?: number
  s30min?: number
  s30max?: number
  stockMin?: number
  stockMax?: number
  priceMin?: number
  priceMax?: number
  search?: string
  page?: number
  limit?: number
}

export interface AdFilters {
  platform?: 'facebook' | 'tiktok'
  countryId?: string
  search?: string
  sortBy?: string
  order?: 'asc' | 'desc'
  page?: number
  limit?: number
}

// Países
export interface Country {
  id: string
  name: string
  code: string
}

export const DROPKILLER_COUNTRIES: Country[] = [
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

export const ADSKILLER_COUNTRIES: Country[] = [
  { id: '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', name: 'Colombia', code: 'CO' },
  { id: '40334494-86fc-4fc0-857a-281816247906', name: 'México', code: 'MX' },
  { id: '1be5939b-f5b1-41ea-8546-fc72a7381c9d', name: 'Ecuador', code: 'EC' },
  { id: '8e7e6e88-2a90-4a8d-b6eb-ed0975c1df59', name: 'Perú', code: 'PE' },
  { id: 'bed193de-9cda-47b7-ab21-fc4abde86bd1', name: 'Chile', code: 'CL' },
  { id: 'e8a05443-3d9c-4a24-93f0-1d197923d1fe', name: 'Argentina', code: 'AR' },
  { id: 'de1f3f37-ed5f-4335-b151-974932bcbd83', name: 'Bolivia', code: 'BO' },
  { id: '3a44b739-d1c1-4fc5-8742-ae691d09c434', name: 'Costa Rica', code: 'CR' },
  { id: '2361e5ee-f992-476c-a380-2a157e384a60', name: 'España', code: 'ES' },
  { id: '10c184e2-c7ac-4cfb-9b7f-e24e71b7588b', name: 'Paraguay', code: 'PY' },
  { id: '13a06d2f-67fe-4c7e-b78d-01e23e68b99e', name: 'Uruguay', code: 'UY' },
  { id: '2109e408-9cb2-488d-8d79-1e0429691682', name: 'Venezuela', code: 'VE' },
]

export const PLATFORMS = [
  'dropi',
  'easydrop', 
  'aliclick',
  'dropea',
  'droplatam',
  'seventy block',
  'wimpy',
  'mastershop',
]
