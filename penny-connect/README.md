# Penny Connect Mark 1

A local-first, framework-free network heartbeat console for the Penny Area Network.

## Current build

Open `index.html` directly or serve the repository and visit `/penny-connect/`.

The console currently provides:

- One-button **PENNY CONNECT** route probe
- Browser, Nexus, S23/Tasker, laptop/PennyCore, Pi, and Roku bridge status cards
- Heartbeat ring that moves only when at least one route is verified
- Local-only endpoint configuration using browser `localStorage`
- Visible probe log and downloadable JSON state packet
- Optional 15-second automatic probe
- **PINK safe mode**, which disables external network requests
- Explicit **Owner Gate** before hotspot requests and route launches
- HTTPS mixed-content detection reported as `BLOCKED`, not falsely marked offline

## Safe test flow

1. Open `penny-connect/index.html`.
2. Press **PENNY CONNECT**.
3. Verify the browser route and public Nexus route.
4. Open **CONFIGURE** and add only trusted health endpoints.
5. Keep passwords, API keys, tokens, and private query parameters out of endpoint URLs.
6. Configure the S23 / Tasker hotspot command URL only after the Tasker bridge exists and is intentionally exposed to the local Penny network.
7. Press **REQUEST HOTSPOT** and confirm the visible Owner Gate.

## Default endpoints

- Nexus: `https://nexus.wildcarddev.com/`
- Laptop/PennyCore: `http://127.0.0.1:8765/health`
- S23, Pi, Roku, and hotspot command: intentionally blank

## Browser boundary

A page loaded over HTTPS cannot probe ordinary HTTP LAN endpoints because browsers block mixed content. For LAN testing, open the file locally or serve it over HTTP on the trusted local network. The console reports this state as `BLOCKED` rather than `OFFLINE`.

Cross-origin probes use credential-free `no-cors` requests. An opaque response proves only that the browser heard a route. It does not authenticate the device or reveal response content.

## Governance

- Additive proposal branch only
- No automatic deployment
- No hidden recording
- No credential storage
- No automatic hotspot, router, Roku, Tasker, watch, Windows, or Home Assistant control
- High-impact actions remain behind Owner Gate
