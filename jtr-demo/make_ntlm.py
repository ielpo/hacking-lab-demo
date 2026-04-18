from passlib.hash import nthash

users = [
    ("marc",  "Marc123"),
    ("alice", "dragon"),
    ("bob",   "P@ssw0rd2024"),
    ("carol", "Winter2024"),
    ("dave",  "xk7m"),
]
with open("ntlm.hashes", "w") as f:
    for u, p in users:
        h = nthash.hash(p)
        f.write(f"{u}:1000:aad3b435b51404eeaad3b435b51404ee:{h}:::\n")
print(open("ntlm.hashes").read())