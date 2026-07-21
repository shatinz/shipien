import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get('Authorization');
  const token = authHeader?.split(' ')[1];

  if (!token || token !== process.env.JWT_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { subscriptionId } = await request.json();

    await prisma.$transaction([
      prisma.paymentReceipt.update({
        where: { subscriptionId },
        data: { status: 'rejected' },
      }),
      prisma.vpnSubscription.update({
        where: { id: subscriptionId },
        data: { status: 'rejected' },
      }),
    ]);

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error('Internal subscription rejection error:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
