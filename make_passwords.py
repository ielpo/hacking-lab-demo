from passlib.hash import nthash
import bcrypt

users = [
    ("marc", "Marc123"),
    ("alice", "dragon"),
    ("bob", "P@ssw0rd2024"),
    ("carol", "Winter2024"),
    ("dave", "xk7m"),
]

with open("ntlm.hashes", "w") as f:
    for u, p in users:
        h = nthash.hash(p)
        f.write(f"{u}:1000:aad3b435b51404eeaad3b435b51404ee:{h}:::\n")

print("NTLM Hashes")
print(open("ntlm.hashes").read())

with open("bcrypt.hashes", "w") as f:
    for u, p in users:
        h = bcrypt.hashpw(bytes(p.encode()), bcrypt.gensalt(rounds=12)).decode()
        f.write(f"{u}:{h}\n")

print("bcrypt Hashes")
print(open("bcrypt.hashes").read())