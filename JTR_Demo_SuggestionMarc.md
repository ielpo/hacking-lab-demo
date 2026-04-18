# John The Ripper
Attention: Uses John Jumbo (not Core)!

## Structure

| Demo                              | Question answered                                | Time   |
| --------------------------------- | ------------------------------------------------ | ------ |
| **1. Mode convergence**           | Which mode wins fastest for which password type? | ~3 min |
| **2. Hash Algorithm Differences** | Why does hash algorithm choice matter?           | ~1 min |

Between each demo, need to run `rm -f ~/.john/john.pot` so cached cracks don't pre-empt the next run.

# Demo 1 — Mode convergence on NTLM hashes

HTLM is format of Windows AD PW hashes + it's fast to compute.

Setup: Build the hash file. NTLM is `MD4(UTF-16LE(password))` (or have that be the one we extract from the server!)

```bash
python make_ntlm.py
```bash
# Download rockyou
[ -f rockyou.txt ] || curl -L -o rockyou.txt https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
gunzip rockyou.txt.gz   
```


## 1.2 Round 1: Single mode only (`--single`)

Single mode; uses the username and account metadata with aggressive mangling rules.

```bash
rm -f ~/.john/john.pot
john --single --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```

**Expected result:** Only `marc:Marc2024!` is cracked.

--> Speach Notes: "One out of five — and notice it's the one where the password is a variant of the username. 
Lesson one: don't base your password on your name."

## 1.3 Round 2: Wordlist, no rules

Pure dictionary attack.

```bash
john --wordlist=rockyou.txt --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```

**Expected result:** `alice:dragon` cracked, plus `marc` still shown from before.

"`dragon` is in the top 100 of rockyou — essentially free to crack. 
Lesson two: if your password is in any public breach dump, it's already compromised."$

## 1.4 Round 3: Wordlist + Jumbo rules

Rules engine — leet substitutions, appended years, capitalizations, the standard 90-ish transformations in the Jumbo ruleset.

```bash
john --wordlist=rockyou.txt --rules=Jumbo --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```

**Expected result:** `bob:P@ssw0rd2024` now falls.

"`P@ssw0rd2024` looks 'strong' — mixed case, numbers, symbols, 12 characters. But it's a dictionary word with predictable substitutions, and the rules engine catches exactly that pattern."

## 1.5 Round 4: Mask mode

"Now suppose we know the corporate password policy — say HR forces everyone to use 'Word + Year'. We encode that as a mask."

```bash
# ?u = upper, ?l = lower, ?d = digit
john --mask='?u?l?l?l?l?l?d?d?d?d' --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```

**Expected result:** `carol:Winter2024` cracked. Mask narrows the keyspace to exactly `Uppercase + 5 lower + 4 digits` = 26 × 26⁵ × 10⁴ ≈ 3 billion candidates

"If the attacker knows anything about your policy — from HR leaks, support tickets, or OSINT — they can prune the search space drastically.".

## 1.6 Round 5: Incremental (brute force)

"Last resort: we give up on any structure and brute-force by character frequency. This is the slowest mode, but it's guaranteed to find anything within its keyspace if you let it run long enough."

```bash
john --incremental=Alnum --min-length=4 --max-length=4 --format=nt ntlm.hashes
john --show --format=nt ntlm.hashes
```

**Expected result:** `dave:xk7m` cracked.

"All five cracked."

# Demo 2 — The defensive flip: bcrypt resists

Same weak password, different hash algorithm.

## 2.1 Generate a bcrypt hash of the same weak password

```bash
python3 -c "import bcrypt; print('user:' + bcrypt.hashpw(b'Summer24!', bcrypt.gensalt(rounds=12)).decode())" > bcrypt.hash
cat bcrypt.hash
```

You'll see something like:

```
user:$2b$12$abcd...verylonghash
```

## 2.2 Attempt the crack

```bash
rm -f ~/.john/john.pot
john --wordlist=rockyou.txt --rules=Single --format=bcrypt bcrypt.hash
```

After 30s, press any key to show status.

```
0g 0:00:00:38  3/3 0g/s 18.5p/s 18.5c/s 18.5C/s ...
```

Now we're at ~20 guesses per second instead of 10 billion.