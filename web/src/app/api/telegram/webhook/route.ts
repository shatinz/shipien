import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { createVpnUser } from '@/lib/vpn';
import { editMessageReplyMarkup } from '@/lib/telegram';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Telegram sends callback_query updates
    if (!body.callback_query) {
      return NextResponse.json({ ok: true });
    }

    const callbackQuery = body.callback_query;
    const data: string = callbackQuery.data || '';
    const messageId: number = callbackQuery.message?.message_id;

    if (!data.includes(':')) {
      return NextResponse.json({ ok: true });
    }

    const [action, subscriptionId] = data.split(':');

    const receipt = await prisma.paymentReceipt.findUnique({
      where: { subscriptionId },
      include: {
        subscription: { include: { plan: true, user: true } },
      },
    });

    if (!receipt) {
      return NextResponse.json({ ok: true });
    }

    if (action === 'approve') {
      // Create VPN user on the server
      const vpnResult = await createVpnUser(
        receipt.subscription.user.username,
        receipt.subscription.plan.duration
      );

      const expiresAt = new Date(Date.now() + receipt.subscription.plan.duration * 86400 * 1000);

      await prisma.paymentReceipt.update({
        where: { subscriptionId },
        data: { status: 'approved' },
      });

      await prisma.vpnSubscription.update({
        where: { id: subscriptionId },
        data: {
          status: 'active',
          config: vpnResult ? JSON.stringify(vpnResult) : null,
          expiresAt,
        },
      });

      // Update Telegram message
      if (messageId) {
        await editMessageReplyMarkup(
          messageId,
          `✅ <b>Approved!</b>\n\n👤 User: <b>${receipt.subscription.user.username}</b>\n📦 Plan: <b>${receipt.subscription.plan.name}</b>\n🆔 Sub ID: <code>${subscriptionId}</code>\n\n✅ VPN config sent to user.`
        );
      }
    } else if (action === 'reject') {
      await prisma.paymentReceipt.update({
        where: { subscriptionId },
        data: { status: 'rejected' },
      });

      await prisma.vpnSubscription.update({
        where: { id: subscriptionId },
        data: { status: 'rejected' },
      });

      if (messageId) {
        await editMessageReplyMarkup(
          messageId,
          `❌ <b>Rejected</b>\n\n👤 User: <b>${receipt.subscription.user.username}</b>\n📦 Plan: <b>${receipt.subscription.plan.name}</b>\n🆔 Sub ID: <code>${subscriptionId}</code>`
        );
      }
    }

    // Answer callback query to remove loading state in Telegram
    await fetch(
      `https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/answerCallbackQuery`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ callback_query_id: callbackQuery.id }),
      }
    );

    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error('Telegram webhook error:', err);
    return NextResponse.json({ ok: true }); // Always return 200 to Telegram
  }
}
