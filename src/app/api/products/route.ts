import { NextRequest, NextResponse } from 'next/server'
import { createDropKillerClient } from '@/lib/dropkiller'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    
    const filters = {
      platform: searchParams.get('platform') || 'dropi',
      country: searchParams.get('country') || '65c75a5f-0c4a-45fb-8c90-5b538805a15a', // Colombia
      s7min: searchParams.get('s7min') ? parseInt(searchParams.get('s7min')!) : undefined,
      s7max: searchParams.get('s7max') ? parseInt(searchParams.get('s7max')!) : undefined,
      s30min: searchParams.get('s30min') ? parseInt(searchParams.get('s30min')!) : undefined,
      s30max: searchParams.get('s30max') ? parseInt(searchParams.get('s30max')!) : undefined,
      stockMin: searchParams.get('stockMin') ? parseInt(searchParams.get('stockMin')!) : undefined,
      stockMax: searchParams.get('stockMax') ? parseInt(searchParams.get('stockMax')!) : undefined,
      priceMin: searchParams.get('priceMin') ? parseInt(searchParams.get('priceMin')!) : undefined,
      priceMax: searchParams.get('priceMax') ? parseInt(searchParams.get('priceMax')!) : undefined,
      search: searchParams.get('search') || undefined,
      page: searchParams.get('page') ? parseInt(searchParams.get('page')!) : 1,
      limit: searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : 30,
    }

    const client = createDropKillerClient()
    const data = await client.getProducts(filters)

    return NextResponse.json(data)
  } catch (error) {
    console.error('Products API Error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch products' },
      { status: 500 }
    )
  }
}
