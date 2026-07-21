# Server Documentation & Status

This file documents the status of the processes and the directory structure on this server to ensure clear communication between developers and agents working on it.

## Network & Architecture
*   **Environment (Intranet-Only):** This server operates on a strict Iran-only Intranet profile.
    *   **Domestic Connections:** Flawless. Ping to domestic sites (e.g., `aparat.com`) is very low (~1.6ms), and HTTP requests succeed immediately.
    *   **International Connections:** Completely blocked. Pings to global IPs (e.g., `8.8.8.8`) drop 100% of packets, and TCP connections to international domains (`google.com`, `crates.io`) time out entirely.
*   **DNS & Anti-Filtering Investigation:**
    *   **403.online:** The datacenter drops all traffic to 403.online IPs (`10.202.10.202`) because they are in a private IP range that conflicts with internal routing. Both UDP port 53 and DoT port 853 fail.
    *   **Shecan:** The server can successfully reach Shecan (`178.22.122.100`) for DNS resolution. However, configuring Shecan does not bypass the restrictions because the datacenter drops the subsequent TCP connection to the international IP returned by Shecan.
*   **Proxy Dependency:** Because physical TCP connections to international IPs are dropped, changing DNS servers will not restore global internet access. A working proxy (like Xray with an active upstream) is strictly required to access the outside world.

## Active Background Processes (VPN & Proxy)
The server has several `tmux` sessions running VPN and proxy software:

1.  **`marz` / `hys` (Marzban Panel):**
    *   Marzban is running via Docker (`marzban-1`).
    *   **Role:** It manages the Xray core proxy. If Xray is killed manually, Marzban will automatically restart it.
2.  **`xray` (Xray Core):**
    *   **Ports:** Listening on SOCKS/HTTP ports `10808` and `1080` (locally bound).
    *   **Status:** Currently **failing**. The upstream node configured in Marzban (e.g., `berimmm.ir` / `91.107.247.163`) is unreachable (100% packet loss). Attempts to route traffic through this proxy will result in a timeout.
3.  **`open` / `snispf` (SNI Spoofer):**
    *   **Port:** Listening on `127.0.0.1:8080`.
    *   **Role:** Used to bypass DPI (Deep Packet Inspection) for SNI filtering.

*Note: There are NO transparent iptables rules in the `nat` or `mangle` tables routing all traffic. The proxies are port-bound.*

## Directory Structure
The `/root` directory has been organized into the following structure:

*   `/root/armitage/` -> Contains the project source code (Frontend/Backend).
*   `/root/vpn_configs/` -> Contains VPN-related configuration and files:
    *   `hy2.yaml` (Hysteria 2 config)
    *   `Client.ovpn` (OpenVPN profile)
    *   `Xray-linux-64.zip` (Xray binaries)
    *   `README.md` & `LICENSE` (Xray documentation)
*   `/root/setup_scripts/` -> Contains system maintenance scripts:
    *   `a.sh` (Disk partition resize script)
*   `/root/SERVER.md` -> This documentation file.

## Modifications Made
*   **Process Stopped:** The failing SSH/Ping test loop to the dead upstream (`berimmm.ir`) running in the `marz` tmux session was halted (`SIGINT`).
*   **Directory Organized:** Loose configuration files and scripts in `/root` were moved to their respective `/root/vpn_configs/` and `/root/setup_scripts/` directories to declutter the workspace.

## Proxy Testing (2026-06-08)
*   **Hysteria 2 Config Test:** Tested a `hy2://` configuration targeting `pics.jibijij.top:27039`. The test **FAILED**. The client logged `connect error: timeout: no recent network activity`, indicating that the proxy connection is either blocked by the firewall/ISP or the remote proxy server is down.

## Automated Proxy Failover Daemon (2026-06-11)
*   **Daemon (`auto_proxy.service`)**: A systemd daemon is running the Python script `/root/setup_scripts/auto_proxy.py`.
*   **Functionality**: It periodically tests multiple Cloudflare Worker BPB `vless://` proxies listed in `/root/vpn_configs/proxies.txt`. If the active connection drops, it auto-switches to the best-performing node and manages a standalone `xray` process.
*   **Local Listener**: The daemon spins up `xray` which binds a local SOCKS5 proxy on `0.0.0.0:10808`.
*   **Marzban Integration**: The `/var/lib/marzban/xray_config.json` outbound was modified. Marzban's Docker container runs in `network_mode: host` and directly routes user outbound traffic through `127.0.0.1:10808`.
*   **IP Hunting**: `SenPaiScanner` was installed globally at `/root/.local/bin/senpaiscanner`. Run it interactively to find new Cloudflare IPs and append them to the `proxies.txt` file.

## Proxy Testing Update (2026-06-25)
*   **DNS Fixed**: System DNS poisoned by ISP was permanently fixed by forcing `8.8.8.8` and `1.1.1.1` in `/etc/resolv.conf` and locked with `chattr +i`.
*   **Hysteria2 Success**: A working `hy2://` configuration targeting `foto.jibijij.top` was established. The `hysteria` client is now running as a persistent systemd service (`hysteria_proxy.service`) on `127.0.0.1:12001`. Marzban is routed through this SOCKS5 proxy to restore user connectivity.

## Shipienbot Deployment Update (2026-06-29)
*   **Application Directory**: Configured at `/root/shipien/` containing `shipienbot.py`, `configs.py`, and `requirements.txt`.
*   **Dependency Setup**: Installed Python dependencies offline from local wheels into `/root/shipien/venv/` (offline to prevent network handshake failures over proxy).
*   **Systemd Integration**: Enabled and started `shipienbot.service` to keep the bot active persistently in the background. Currently active and running.
*   **Credentials**: Configured with the admin ID (`8373593549`) and correct bot token.

