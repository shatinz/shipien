import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const b64Link = searchParams.get('c');
    
    if (!b64Link) {
      return new NextResponse('Missing config', { status: 400 });
    }

    // A standard Base64 subscription endpoint simply returns the Base64 list of connections.
    // Since 'c' query parameter is already the Base64 representation of the connection link,
    // we can return it directly.
    return new NextResponse(b64Link, {
      status: 200,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
      },
    });
  } catch (err) {
    console.error('Error serving direct Base64 sub:', err);
    return new NextResponse('Internal error', { status: 500 });
  }
}
