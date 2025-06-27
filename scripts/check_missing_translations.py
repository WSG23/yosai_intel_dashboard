#!/usr/bin/env python3
"""Check for missing translations in .po files."""
import os
import sys


def check_po_file(path: str) -> list[str]:
    missing = []
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    msgid = None
    for line in lines:
        line = line.strip()
        if line.startswith("msgid "):
            msgid = line[len("msgid "):].strip().strip('"')
        elif line.startswith("msgstr ") and msgid is not None:
            msgstr = line[len("msgstr "):].strip().strip('"')
            if msgid and not msgstr:
                missing.append(msgid)
            msgid = None
    return missing


def main() -> int:
    base_dir = os.path.join(os.path.dirname(__file__), os.pardir, "translations")
    errors = 0
    for root, _, files in os.walk(base_dir):
        for fname in files:
            if fname.endswith(".po"):
                path = os.path.join(root, fname)
                missing = check_po_file(path)
                if missing:
                    print(f"Missing translations in {path}:")
                    for m in missing:
                        print(f"  - {m}")
                    errors += 1
    if errors:
        print("\nTranslation check failed")
        return 1
    else:
        print("All translations present")
        return 0


if __name__ == "__main__":
    sys.exit(main())
