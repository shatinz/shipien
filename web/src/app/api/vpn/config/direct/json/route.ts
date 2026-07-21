import { NextRequest, NextResponse } from 'next/server';
import { parseAnytlsLink, generateSingBoxConfig } from '@/lib/singbox';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const b64Link = searchParams.get('c');
    
    if (!b64Link) {
      return NextResponse.json({ error: 'Missing configuration parameter' }, { status: 400 });
    }

    let anytlsLink: string;
    try {
      anytlsLink = Buffer.from(b64Link, 'base64').toString('utf-8');
    } catch {
      return NextResponse.json({ error: 'Invalid encoding' }, { status: 400 });
    }

    const parsedOptions = parseAnytlsLink(anytlsLink);
    if (!parsedOptions) {
      return NextResponse.json({ error: 'Invalid config link or unsupported protocol' }, { status: 400 });
    }

    const singBoxConfig = generateSingBoxConfig(parsedOptions);

    return new NextResponse(JSON.stringify(singBoxConfig, null, 2), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Content-Disposition': 'attachment; filename="shipien-config.json"',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
      },
    });
  } catch (err) {
    console.error('Error downloading direct JSON file:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
