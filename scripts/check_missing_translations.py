import sys


def main() -> None:
    missing = []
    msgid = None
    msgstr = None
    with open("translations/ja/LC_MESSAGES/messages.po", encoding="utf-8") as f:
        for line in f:
            if line.startswith("msgid "):
                msgid = line[len("msgid ") :].strip().strip('"')
                msgstr = None
            elif line.startswith("msgstr "):
                msgstr = line[len("msgstr ") :].strip().strip('"')
                if msgid and not msgstr:
                    missing.append(msgid)
    if missing:
        print("Missing translations:", missing)
        sys.exit(1)
    print("All translations present")


if __name__ == "__main__":
    main()
