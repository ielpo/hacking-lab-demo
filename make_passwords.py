import csv

import bcrypt
from passlib.hash import nthash


def load_users(path: str) -> list[tuple[str, str]]:
    with open(path, newline="") as handle:
        reader = csv.DictReader(handle)
        return [(row["username"], row["password"]) for row in reader]


users = load_users("demo_users.csv")

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