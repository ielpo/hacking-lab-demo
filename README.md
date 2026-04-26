# Hacking Lab Demo

A Docker Compose lab for demonstrating John the Ripper and Hydra against services with different authentication methods.

## Prerequisites

- Docker and Docker Compose
- uv

# Quick Start

```bash
gunzip rockyou.txt.gz
uv run make_passwords.py
docker compose up -d
```

## Services

| Service | Protocol | Host Port | Credentials |
|---|---|---|---|
| Samba | SMB | 4450 | `alice` / `dragon` |
| SSH | SSH | 2222 | `admin` / `password123` |
| HTTP Basic Auth | HTTP | 8080 | `webadmin` / `dragon` |

## Accessing Services

- **SSH:** `ssh admin@localhost -p 2222`
- **Samba:** `smbclient -L //127.0.0.1 -p 4450 -U 'alice%dragon'`
- **HTTP Basic Auth:** open <http://localhost:8080> in a browser

## Cleanup

```bash
docker compose down -v
```

# Hydra Demo

## SSH — password-list attack

Command:
```bash
hydra -l admin -P rockyou.txt -t 10 -f -V -s 2222 127.0.0.1 ssh
```

## SMB — password-list attack

Command:
```bash
hydra -l alice -P rockyou.txt -t 8 -f -V smb://127.0.0.1:4450
```

## HTTP Basic Auth — password-list attack

Command:
```bash
hydra -l webadmin -P rockyou.txt -t 64 -f -V -s 8080 127.0.0.1 http-get /
```

# John The Ripper

Requires John Jumbo (not Core) for the full ruleset and masks used here.

Table (quick glance)
| Demo | Purpose | Approx time |
|------|---------|------------:|
| Mode convergence | Show how different modes target different password types | ~3 min |
| Algorithm comparison | Show speed difference (NTLM vs bcrypt) | ~1 min |

## Demo 1 — Mode convergence (NTLM)

Build hashes (if not already present):
```bash
uv run make_passwords.py
```

Run these rounds in order, clearing `john.pot` between rounds so previous cracks don't affect results.

1) Single mode (targets username-based variants)
```bash
rm -f ~/.john/john.pot
john --single --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```
Expected: `marc:Marc123`

2) Wordlist (no rules)
```bash
rm -f ~/.john/john.pot
john --wordlist=rockyou.txt --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```
Expected: `alice:dragon`

3) Incremental (brute-force)
```bash
rm -f ~/.john/john.pot
john --incremental=Alnum --min-length=4 --max-length=4 --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```
Expected: `dave:xk7m`

4) Wordlist + Jumbo rules
```bash
rm -f ~/.john/john.pot
john --wordlist=rockyou.txt --rules=Jumbo --users=bob --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```
Expected: `bob:P@ssw0rd2024`

5) Mask mode (policy-driven)
```bash
rm -f ~/.john/john.pot
# ?u = upper, ?l = lower, ?d = digit
john --mask='?u?l?l?d?d?d?d' --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```
Expected: `carol:Winter2024`

## Demo 2 — Hash algorithm differences (bcrypt)

Crack attempt:
```bash
rm -f ~/.john/john.pot
john --wordlist=rockyou.txt --rules=Single --format=bcrypt bcrypt.hashes
```
