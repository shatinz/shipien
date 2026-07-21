import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
  try {
    const plans = await prisma.vpnPlan.findMany({
      where: { active: true },
      orderBy: { sortOrder: 'asc' },
    });

    const parsedPlans = plans.map((p) => ({
      ...p,
      features: JSON.parse(p.features) as string[],
    }));

    return NextResponse.json({ plans: parsedPlans });
  } catch {
    return NextResponse.json({ error: 'Failed to fetch plans' }, { status: 500 });
  }
}
