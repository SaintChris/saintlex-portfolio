# Android Linux Homelab Case Study

## Status

Sanitized portfolio case study derived from a private historical lab. The original repository remains private because its history contains operational material that should not be published without a full secret/history review.

## Objective

Continue practicing Linux-style system administration and web hosting after losing access to a conventional homelab machine by repurposing a Samsung Galaxy S7 as a constrained server platform.

## Constraints

- Legacy mobile hardware
- Android environment without rooting or a custom ROM
- Limited memory, CPU, storage, and thermal headroom
- Preference for free/open-source tooling
- No inbound firewall-port exposure for the public web path

## Architecture

```text
Samsung Galaxy S7
    ↓
Android + Termux
    ↓
Nginx
    ↓
PHP-FPM
    ↓
MariaDB
    ↓
WordPress / static web content

Remote access path
    ↓
Cloudflare Tunnel
    ↓
Public web endpoint
```

Additional lab work included service monitoring, backups, scripting, diagnostics, and resource-conscious configuration.

## Technologies

- Android / Termux
- Nginx
- PHP-FPM
- MariaDB
- WordPress
- Cloudflare Tunnel
- Cloudflare Turnstile
- shell scripting
- Python utilities
- Docker experiments
- Grafana / Prometheus experiments
- Uptime Kuma experiments
- Ansible experiments

## Engineering lessons

### Resource constraints change design decisions

Mobile hardware forces explicit trade-offs around process count, memory use, storage writes, thermals, and unnecessary services.

### Tunneling can reduce exposed attack surface

A tunnel-based ingress model allowed the lab to avoid directly forwarding local inbound ports. That does not remove the need for application, credential, and host security controls.

### Reproducibility matters more than a one-off success

The useful part of the lab was not simply getting a webpage online. The stronger learning came from documenting services, automation, diagnostics, backup/recovery ideas, and failure modes.

### Historical repositories can become unsafe portfolio artifacts

Operational labs tend to accumulate logs, backups, certificates, configuration files, command history, and access material. A sanitized derivative case study is safer than making the historical repository public.

## Publication boundary

Not included here:

- credentials or tokens
- private keys or certificates
- tunnel configuration secrets
- IP addresses or private network details
- SQL backups
- command history
- raw security scans
- internal logs
- personal data

The private source repository is retained as historical evidence and should only be considered for publication after a dedicated Git-history and secret-scanning review.
