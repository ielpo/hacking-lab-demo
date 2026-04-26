import bcrypt
from passlib.hash import nthash

users = [
    ("marc", "Marc123"),
    ("alice", "dragon"),
    ("bob", "P@ssw0rd2024"),
    ("carol", "Wind2024"),
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

with open("users.conf", "w") as f:
    uid = 2000
    for u, p in users:
        f.write(f"{u}:{uid}:smb:1000:{p}\n")
        uid += 1

print("SMB users")
print(open("users.conf").read())
