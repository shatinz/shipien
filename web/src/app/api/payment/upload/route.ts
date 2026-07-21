import { NextRequest, NextResponse } from 'next/server';
import { getSession } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { sendAdminReceiptWithButtons } from '@/lib/telegram';

export async function POST(request: NextRequest) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { subscriptionId, receiptData, receiptType, configName } = await request.json();

    // Validate subscription belongs to user
    const subscription = await prisma.vpnSubscription.findFirst({
      where: { id: subscriptionId, userId: session.userId },
      include: { plan: true },
    });

    if (!subscription) {
      return NextResponse.json({ error: 'Subscription not found' }, { status: 404 });
    }

    if (subscription.status !== 'pending') {
      return NextResponse.json({ error: 'Subscription is not pending payment' }, { status: 400 });
    }

    // Save configName in subscription config json
    if (configName) {
      await prisma.vpnSubscription.update({
        where: { id: subscriptionId },
        data: {
          config: JSON.stringify({ configName: configName.toLowerCase() }),
        },
      });
    }

    // Check if receipt already exists
    const existingReceipt = await prisma.paymentReceipt.findUnique({
      where: { subscriptionId },
    });
    if (existingReceipt) {
      return NextResponse.json({ error: 'Receipt already uploaded for this subscription' }, { status: 409 });
    }

    // Create receipt record
    const receipt = await prisma.paymentReceipt.create({
      data: {
        userId: session.userId,
        subscriptionId,
        receiptData,
        receiptType: receiptType || 'text',
        status: 'pending',
      },
    });

    // Notify admin via Telegram
    try {
      const telegramResult = await sendAdminReceiptWithButtons(
        subscriptionId,
        session.username,
        subscription.plan.name,
        receiptData,
        receiptType || 'text',
        configName
      );

      if (telegramResult.ok && telegramResult.result) {
        await prisma.paymentReceipt.update({
          where: { id: receipt.id },
          data: { telegramMsgId: telegramResult.result.message_id },
        });
      }
    } catch (tgErr) {
      console.error('Telegram notification failed:', tgErr);
      // Don't fail the request if Telegram is down
    }

    return NextResponse.json({ success: true, receiptId: receipt.id });
  } catch (err) {
    console.error('Payment upload error:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
