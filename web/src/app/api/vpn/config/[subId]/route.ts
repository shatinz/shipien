import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { parseAnytlsLink, generateSingBoxConfig } from '@/lib/singbox';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ subId: string }> }
) {
  const { subId } = await params;

  try {
    const subscription = await prisma.vpnSubscription.findUnique({
      where: { id: subId },
    });

    if (!subscription || subscription.status !== 'active' || !subscription.config) {
      return NextResponse.json({ error: 'Configuration not found' }, { status: 404 });
    }

    let configData;
    try {
      configData = JSON.parse(subscription.config);
    } catch {
      return NextResponse.json({ error: 'Invalid config format' }, { status: 500 });
    }

    const clientName = configData?.clientName;
    if (clientName) {
      try {
        const panelRes = await fetch(`http://108.61.198.98:2096/sub/${clientName}?format=json`, {
          headers: { 'Host': 'h2.morningislighting.ir' },
          next: { revalidate: 60 } // cache for 1 minute
        });
        if (panelRes.ok) {
          const panelJson = await panelRes.json();
          return new NextResponse(JSON.stringify(panelJson, null, 2), {
            status: 200,
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*',
            },
          });
        }
      } catch (err) {
        console.error('Failed to proxy panel json, falling back to builder:', err);
      }
    }

    const anytlsLink = configData?.links?.[0];
    if (!anytlsLink) {
      return NextResponse.json({ error: 'Config link not found' }, { status: 404 });
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
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
      },
    });
  } catch (err) {
    console.error('Error fetching sing-box JSON config:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
