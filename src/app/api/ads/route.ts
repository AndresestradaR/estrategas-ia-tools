import { NextRequest, NextResponse } from 'next/server'
import { createDropKillerClient } from '@/lib/dropkiller'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    
    const filters = {
      platform: (searchParams.get('platform') as 'facebook' | 'tiktok') || 'facebook',
      countryId: searchParams.get('countryId') || '10ba518f-80f3-4b8e-b9ba-1a8b62d40c47', // Colombia
      search: searchParams.get('search') || '',
      sortBy: searchParams.get('sortBy') || 'updated_at',
      order: (searchParams.get('order') as 'asc' | 'desc') || 'desc',
      page: searchParams.get('page') ? parseInt(searchParams.get('page')!) : 1,
      limit: searchParams.get('limit') ? parseInt(searchParams.get('limit')!) : 30,
    }

    const client = createDropKillerClient()
    const data = await client.getAds(filters)

    return NextResponse.json(data)
  } catch (error) {
    console.error('Ads API Error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch ads' },
      { status: 500 }
    )
  }
}
