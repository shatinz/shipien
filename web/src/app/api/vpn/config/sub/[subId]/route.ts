import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

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
      return new NextResponse('Config not found', { status: 404 });
    }

    let configData;
    try {
      configData = JSON.parse(subscription.config);
    } catch {
      return new NextResponse('Invalid format', { status: 500 });
    }

    const clientName = configData?.clientName;
    if (clientName) {
      try {
        const panelRes = await fetch(`http://108.61.198.98:2096/sub/${clientName}`, {
          headers: { 'Host': 'h2.morningislighting.ir' },
          next: { revalidate: 60 }
        });
        if (panelRes.ok) {
          const panelText = await panelRes.text();
          return new NextResponse(panelText, {
            status: 200,
            headers: {
              'Content-Type': 'text/plain; charset=utf-8',
              'Access-Control-Allow-Origin': '*',
            },
          });
        }
      } catch (err) {
        console.error('Failed to proxy panel sub list, falling back to builder:', err);
      }
    }

    const anytlsLink = configData?.links?.[0];
    if (!anytlsLink) {
      return new NextResponse('Link not found', { status: 404 });
    }

    // In dynamic overrides, we translate IP to domain
    const rawUrl = anytlsLink.replace('anytls://', '');
    const [authAndHost, queryAndFragment] = rawUrl.split('?');
    const [auth, hostAndPort] = authAndHost.split('@');
    const [server, portStr] = hostAndPort.split(':');
    const password = auth;
    const server_port = parseInt(portStr) || 443;

    const finalServer = (server === '136.244.111.62' || server === '108.61.198.98') 
      ? 'h2.morningislighting.ir' 
      : server;

    const finalLink = `anytls://${password}@${finalServer}:${server_port}?${queryAndFragment || ''}`;
    const b64Response = Buffer.from(finalLink).toString('base64');

    return new NextResponse(b64Response, {
      status: 200,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
      },
    });
  } catch (err) {
    console.error('Error serving subId Base64 sub:', err);
    return new NextResponse('Internal error', { status: 500 });
  }
}
