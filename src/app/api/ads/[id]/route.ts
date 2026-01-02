import { NextRequest, NextResponse } from 'next/server'
import { createDropKillerClient } from '@/lib/dropkiller'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const adId = params.id

    const client = createDropKillerClient()
    const data = await client.getAdDetail(adId)

    return NextResponse.json({
      ad: data.ad || data
    })
  } catch (error) {
    console.error('Ad Detail API Error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch ad detail' },
      { status: 500 }
    )
  }
}
