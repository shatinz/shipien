import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding VPN plans...');

  const plans = [
    {
      name: 'Free Trial',
      price: 0,
      duration: 1,
      bandwidth: '1 GB',
      description: 'Test our connection speed and stability.',
      features: JSON.stringify([
        '1 GB High-Speed Traffic',
        '1 Day Duration',
        'anytls (sing-box) Protocol',
        'No Payment Required',
        'Support via Telegram @shipien',
      ]),
      sortOrder: 1,
    },
    {
      name: '30 GB Premium',
      price: 150000,
      duration: 30,
      bandwidth: '30 GB',
      description: 'High-speed, stable config for casual users.',
      features: JSON.stringify([
        '30 GB Premium Traffic',
        '30 Days Duration',
        'anytls (sing-box) Protocol',
        'Unlimited Speed',
        'Multi-device Support',
        'Priority Support via Telegram @shipien',
      ]),
      sortOrder: 2,
    },
    {
      name: '50 GB Premium',
      price: 200000,
      duration: 30,
      bandwidth: '50 GB',
      description: 'Best choice for streaming and daily browsing.',
      features: JSON.stringify([
        '50 GB Premium Traffic',
        '30 Days Duration',
        'anytls (sing-box) Protocol',
        'Unlimited Speed',
        'Multi-device Support',
        'Priority Support via Telegram @shipien',
      ]),
      sortOrder: 3,
    },
    {
      name: 'Unlimited Premium',
      price: 250000,
      duration: 30,
      bandwidth: 'Unlimited',
      description: 'Ultimate freedom with zero bandwidth caps.',
      features: JSON.stringify([
        'Unlimited Traffic',
        '30 Days Duration',
        'anytls (sing-box) Protocol',
        'Dedicated Server Route',
        'Multi-device Support',
        '24/7 Support via Telegram @shipien',
      ]),
      sortOrder: 4,
    },
  ];

  for (const plan of plans) {
    const existing = await prisma.vpnPlan.findFirst({
      where: { name: plan.name },
    });

    if (existing) {
      await prisma.vpnPlan.update({
        where: { id: existing.id },
        data: plan,
      });
      console.log(`Updated plan: ${plan.name}`);
    } else {
      await prisma.vpnPlan.create({ data: plan });
      console.log(`Created plan: ${plan.name}`);
    }
  }

  console.log('✅ Seeding completed successfully');
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
