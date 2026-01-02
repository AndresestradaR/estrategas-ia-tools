import { ProductFilters, AdFilters } from '@/types'

const DROPKILLER_BASE_URL = 'https://app.dropkiller.com'
const DROPKILLER_API_URL = 'https://extension-api.dropkiller.com'

// Cliente para DropKiller Dashboard (requiere sesión)
export class DropKillerClient {
  private sessionToken: string

  constructor(sessionToken: string) {
    this.sessionToken = sessionToken
  }

  private async fetch(url: string, options: RequestInit = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Cookie': `__session=${this.sessionToken}`,
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`DropKiller API error: ${response.status}`)
    }

    return response.json()
  }

  // Obtener productos con filtros
  async getProducts(filters: ProductFilters = {}) {
    const params = new URLSearchParams()
    
    if (filters.platform) params.set('platform', filters.platform)
    if (filters.country) params.set('country', filters.country)
    if (filters.s7min) params.set('s7min', filters.s7min.toString())
    if (filters.s7max) params.set('s7max', filters.s7max.toString())
    if (filters.s30min) params.set('s30min', filters.s30min.toString())
    if (filters.s30max) params.set('s30max', filters.s30max.toString())
    if (filters.stockMin) params.set('stock-min', filters.stockMin.toString())
    if (filters.stockMax) params.set('stock-max', filters.stockMax.toString())
    if (filters.priceMin) params.set('price-min', filters.priceMin.toString())
    if (filters.priceMax) params.set('price-max', filters.priceMax.toString())
    if (filters.search) params.set('search', filters.search)
    
    params.set('page', (filters.page || 1).toString())
    params.set('limit', (filters.limit || 30).toString())

    const url = `${DROPKILLER_BASE_URL}/dashboard/products?${params.toString()}`
    return this.fetch(url)
  }

  // Obtener detalle de producto
  async getProductDetail(productId: string, platform: string = 'dropi') {
    const url = `${DROPKILLER_BASE_URL}/dashboard/tracking/detail/${productId}?platform=${platform}`
    return this.fetch(url)
  }

  // Obtener anuncios de Adskiller
  async getAds(filters: AdFilters = {}) {
    const body = {
      platform: filters.platform || 'facebook',
      enabled: true,
      sortBy: filters.sortBy || 'updated_at',
      order: filters.order || 'desc',
      countryId: filters.countryId || '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', // Colombia default
      search: filters.search || '',
      page: filters.page || 1,
      limit: filters.limit || 30,
    }

    const url = `${DROPKILLER_BASE_URL}/dashboard/adskiller`
    return this.fetch(url, {
      method: 'POST',
      body: JSON.stringify(body),
    })
  }

  // Obtener detalle de anuncio
  async getAdDetail(adId: string) {
    const url = `${DROPKILLER_BASE_URL}/dashboard/adskiller?analytics=${adId}`
    return this.fetch(url)
  }
}

// Cliente público (sin auth) para historial de ventas
export async function getProductHistory(productIds: string[], country: string = 'CO') {
  const ids = productIds.join(',')
  const url = `${DROPKILLER_API_URL}/api/v3/history?ids=${ids}&country=${country}`
  
  const response = await fetch(url)
  
  if (!response.ok) {
    throw new Error(`DropKiller Public API error: ${response.status}`)
  }
  
  return response.json()
}

// Función helper para crear el cliente
export function createDropKillerClient() {
  const sessionToken = process.env.DROPKILLER_SESSION_TOKEN
  
  if (!sessionToken) {
    throw new Error('DROPKILLER_SESSION_TOKEN not configured')
  }
  
  return new DropKillerClient(sessionToken)
}
