/**
 * Marzban VPN panel API integration
 * Docs: https://github.com/Gozargah/Marzban
 */

const VPN_SERVER_URL = process.env.VPN_SERVER_URL || 'https://vip-03.fl-sub.site:2096';
const VPN_SERVER_TOKEN = process.env.VPN_SERVER_TOKEN || '';

interface MarzbanUser {
  username: string;
  proxies: Record<string, unknown>;
  inbounds: Record<string, string[]>;
  expire: number | null;
  data_limit: number | null;
  data_limit_reset_strategy: string;
  status: string;
  links: string[];
  subscription_url: string;
}

export async function createVpnUser(
  username: string,
  durationDays: number,
  dateLimitGB: number = 50
): Promise<{ links: string[]; subscriptionUrl: string } | null> {
  if (!VPN_SERVER_URL || !VPN_SERVER_TOKEN) {
    console.warn('VPN server not configured');
    return null;
  }

  try {
    const expireTimestamp = Math.floor(Date.now() / 1000) + durationDays * 86400;

    const res = await fetch(`${VPN_SERVER_URL}/api/user`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${VPN_SERVER_TOKEN}`,
      },
      body: JSON.stringify({
        username: `shipien_${username}_${Date.now()}`,
        proxies: { vmess: {}, vless: {}, trojan: {} },
        inbounds: {},
        expire: expireTimestamp,
        data_limit: dateLimitGB * 1024 * 1024 * 1024,
        data_limit_reset_strategy: 'no_reset',
        status: 'active',
      }),
    });

    if (!res.ok) {
      console.error('Marzban API error:', res.status, await res.text());
      return null;
    }

    const data: MarzbanUser = await res.json();
    return {
      links: data.links,
      subscriptionUrl: data.subscription_url,
    };
  } catch (err) {
    console.error('VPN server request failed:', err);
    return null;
  }
}

export async function getVpnUserStatus(vpnUsername: string): Promise<string | null> {
  if (!VPN_SERVER_URL || !VPN_SERVER_TOKEN) return null;

  try {
    const res = await fetch(`${VPN_SERVER_URL}/api/user/${vpnUsername}`, {
      headers: { Authorization: `Bearer ${VPN_SERVER_TOKEN}` },
    });
    if (!res.ok) return null;
    const data: MarzbanUser = await res.json();
    return data.status;
  } catch {
    return null;
  }
}
