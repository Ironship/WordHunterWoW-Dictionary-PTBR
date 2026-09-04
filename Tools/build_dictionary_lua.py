#!/usr/bin/env python3
import argparse, json, pathlib
from pack_config import LOCALES

ROOT = pathlib.Path(__file__).resolve().parents[1]

def quote(value):
    return '"' + str(value or "").replace('\\', '\\\\').replace('"', '\\"').replace('\r', '').replace('\n', '\\n') + '"'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", choices=LOCALES, default=next(iter(LOCALES)))
    parser.add_argument("--all", action="store_true",
                        help="ship every cached word, including ones no longer "
                             "in the corpus")
    args = parser.parse_args()
    config = LOCALES[args.locale]

    # An entry is dropped only when it is both absent from the corpus and reads
    # English-to-English -- the -> the, default -> Default. Those came from
    # quest rows that were never translated, which build_wordlist.py now skips.
    #
    # Absence from the corpus is not on its own a reason to drop anything. The
    # curated file holds words a fuller corpus once carried, and a player who
    # meets one in text this corpus happens not to include should still be able
    # to look it up.
    wordlist = ROOT / f"Data/cache/wordlist_{args.locale}.jsonl"
    live = None
    if wordlist.exists() and not args.all:
        live = {json.loads(line)["key"]
                for line in wordlist.read_text(encoding="utf-8").splitlines()
                if line.strip()}

    def english_leftover(record):
        if live is None or record.get("key") in live:
            return False
        return (record.get("translation") or "").strip().casefold() == \
            (record.get("word") or "").strip().casefold()

    records = {}
    sources = [ROOT / f"Data/cache/translations_{args.locale}_en.jsonl"]
    curated = config.get("curated")
    if curated: sources.append(ROOT / "Data" / curated)
    # Curated entries are read last so a hand-checked gloss wins over the machine one.
    for source in sources:
        if not source.exists(): continue
        for line in source.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip(): continue
            record = json.loads(line)
            if english_leftover(record): continue
            if record.get("translation"): records[record["key"]] = record
    # WoW Lua 5.1: 2^18-1 constants per function. Nested functions avoid
    # "constant table overflow" once unique strings pass that cap.
    chunk = 20000
    keys = sorted(records)
    var = config["variable"]
    lines = [f"{var} = {var} or {{}}"]
    for i in range(0, len(keys), chunk):
        lines.append(";(function()")
        for key in keys[i:i + chunk]:
            record = records[key]
            lines.append(f"{var}[{quote(key)}] = {{ word = {quote(record['word'])}, translation = {quote(record['translation'])}, note = {quote(record.get('note'))} }}")
        lines.append("end)()")
    target = ROOT / "Data" / config["output"]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"locale={args.locale} entries={len(records)} output={target}")

if __name__ == "__main__": main()
