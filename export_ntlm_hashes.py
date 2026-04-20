#!/usr/bin/env python3

from __future__ import annotations

import ldb


LM_PLACEHOLDER = "aad3b435b51404eeaad3b435b51404ee"
SEARCH_FILTER = "(&(objectClass=user)(sAMAccountName=*)(!(sAMAccountName=krbtgt)))"


def as_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def main() -> int:
    database = ldb.Ldb("ldb:///var/lib/samba/private/sam.ldb")
    results = database.search(
        base="",
        scope=ldb.SCOPE_SUBTREE,
        expression=SEARCH_FILTER,
        attrs=["sAMAccountName", "unicodePwd"],
    )

    rows: list[tuple[str, str]] = []
    for result in results:
        username = as_text(result["sAMAccountName"][0])
        if username.endswith("$"):
            continue

        nthash = bytes(result["unicodePwd"][0]).hex()
        rows.append((username, nthash))

    for username, nthash in sorted(rows):
        print(f"{username}:1000:{LM_PLACEHOLDER}:{nthash}:::")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())