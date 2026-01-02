import { NextRequest, NextResponse } from 'next/server'
import { createDropKillerClient, getProductHistory } from '@/lib/dropkiller'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const productId = params.id
    const searchParams = request.nextUrl.searchParams
    const platform = searchParams.get('platform') || 'dropi'

    const client = createDropKillerClient()
    
    // Get product detail
    const productData = await client.getProductDetail(productId, platform)
    
    // Try to get history (public API)
    let history = []
    try {
      const historyData = await getProductHistory([productId])
      history = historyData?.history || []
    } catch (e) {
      console.log('Could not fetch history:', e)
    }

    return NextResponse.json({
      product: productData.product || productData,
      history
    })
  } catch (error) {
    console.error('Product Detail API Error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch product detail' },
      { status: 500 }
    )
  }
}
