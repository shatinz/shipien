import { PrismaClient } from '@prisma/client';
import * as fs from 'fs';
import * as path from 'path';

const prisma = new PrismaClient();

async function main() {
  const mappingPath = path.join(__dirname, '../../../temp_mapping_utf8.json');
  if (!fs.existsSync(mappingPath)) {
    console.error('Error: temp_mapping_utf8.json not found');
    process.exit(1);
  }

  const mapping = JSON.parse(fs.readFileSync(mappingPath, 'utf8'));
  console.log(`Loaded ${Object.keys(mapping).length} client mappings from SQLite.`);

  const subscriptions = await prisma.vpnSubscription.findMany({
    where: { status: 'active' },
  });

  console.log(`Found ${subscriptions.length} active subscriptions in PostgreSQL.`);

  let updatedCount = 0;

  for (const sub of subscriptions) {
    if (!sub.config) continue;
    try {
      const configData = JSON.parse(sub.config);
      const anytlsLink = configData?.links?.[0];
      if (!anytlsLink) continue;

      // Extract password
      const rawUrl = anytlsLink.replace('anytls://', '');
      const [authAndHost] = rawUrl.split('?');
      const [password] = authAndHost.split('@');

      const clientName = mapping[password];
      if (clientName) {
        // Only update if clientName is not already set or is different
        if (configData.clientName !== clientName) {
          configData.clientName = clientName;
          await prisma.vpnSubscription.update({
            where: { id: sub.id },
            data: {
              config: JSON.stringify(configData),
            },
          });
          console.log(`Updated subscription ${sub.id}: set clientName = ${clientName}`);
          updatedCount++;
        }
      } else {
        console.warn(`Warning: No client name mapping found for password: ${password} (Sub ID: ${sub.id})`);
      }
    } catch (err) {
      console.error(`Error processing sub ${sub.id}:`, err);
    }
  }

  console.log(`Successfully updated ${updatedCount} subscriptions.`);
}

main()
  .catch((err) => {
    console.error(err);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
