import { NextRequest } from 'next/server';

export interface SingBoxConfigOptions {
  server: string;
  server_port: number;
  password: string;
  server_name: string;
  node_tag?: string;
}

export function parseAnytlsLink(anytlsLink: string): SingBoxConfigOptions | null {
  if (!anytlsLink.startsWith('anytls://')) {
    return null;
  }

  try {
    const rawUrl = anytlsLink.replace('anytls://', '');
    const [authAndHost, queryAndFragment] = rawUrl.split('?');
    const [auth, hostAndPort] = authAndHost.split('@');
    const [server, portStr] = hostAndPort.split(':');
    const password = auth;
    const server_port = parseInt(portStr) || 443;

    // Dynamically override server IP with domain name if it is any of the raw IPs
    const finalServer = (server === '136.244.111.62' || server === '108.61.198.98') 
      ? 'h2.morningislighting.ir' 
      : server;

    // Parse query params to find SNI/server_name and fragment for node tag
    let server_name = finalServer;
    let node_tag = 'anytls-node';

    if (queryAndFragment) {
      const [query, fragment] = queryAndFragment.split('#');
      if (fragment) {
        node_tag = decodeURIComponent(fragment);
      }
      const paramsList = query.split('&');
      for (const p of paramsList) {
        const [k, v] = p.split('=');
        if (k === 'sni' && v) {
          server_name = decodeURIComponent(v);
        }
      }
    }

    return {
      server: finalServer,
      server_port,
      password,
      server_name,
      node_tag,
    };
  } catch (err) {
    console.error('Error parsing anytls link:', err);
    return null;
  }
}

export function generateSingBoxConfig(options: SingBoxConfigOptions): any {
  const nodeTag = options.node_tag || 'anytls-node';
  
  return {
    inbounds: [
      {
        type: 'tun',
        address: [
          '172.19.0.1/30',
          'fdfe:dcba:9876::1/126'
        ],
        auto_route: true,
        endpoint_independent_nat: false,
        mtu: 9000,
        platform: {
          http_proxy: {
            enabled: true,
            server: '127.0.0.1',
            server_port: 2080
          }
        },
        stack: 'system',
        strict_route: false
      },
      {
        type: 'mixed',
        listen: '127.0.0.1',
        listen_port: 2080,
        users: []
      }
    ],
    outbounds: [
      {
        type: 'selector',
        tag: 'proxy',
        outbounds: [
          'auto',
          'direct',
          nodeTag
        ]
      },
      {
        type: 'urltest',
        tag: 'auto',
        outbounds: [
          nodeTag
        ],
        url: 'http://www.gstatic.com/generate_204',
        interval: '10m',
        tolerance: 50
      },
      {
        type: 'direct',
        tag: 'direct'
      },
      {
        type: 'anytls',
        tag: nodeTag,
        server: options.server,
        server_port: options.server_port,
        password: options.password,
        tls: {
          enabled: true,
          server_name: options.server_name
        }
      }
    ],
    route: {
      auto_detect_interface: true,
      final: 'proxy',
      rules: [
        {
          action: 'sniff'
        },
        {
          action: 'route',
          clash_mode: 'Direct',
          outbound: 'direct'
        },
        {
          action: 'route',
          clash_mode: 'Global',
          outbound: 'proxy'
        }
      ]
    }
  };
}
