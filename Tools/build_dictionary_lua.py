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

    # Only words the corpus still contains are shipped. The translation cache
    # keeps everything ever looked up, including the English words that came
    # from untranslated quest rows before build_wordlist.py learned to skip
    # them; shipping those puts English-to-English entries in a dictionary the
    # player opens to look up their own language.
    wordlist = ROOT / f"Data/cache/wordlist_{args.locale}.jsonl"
    live = None
    if wordlist.exists() and not args.all:
        live = {json.loads(line)["key"]
                for line in wordlist.read_text(encoding="utf-8").splitlines()
                if line.strip()}

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
            if live is not None and record.get("key") not in live: continue
            if record.get("translation"): records[record["key"]] = record
    lines = [f"{config['variable']} = {config['variable']} or {{}}"]
    for key in sorted(records):
        record = records[key]
        lines.append(f"{config['variable']}[{quote(key)}] = {{ word = {quote(record['word'])}, translation = {quote(record['translation'])}, note = {quote(record.get('note'))} }}")
    target = ROOT / "Data" / config["output"]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"locale={args.locale} entries={len(records)} output={target}")

if __name__ == "__main__": main()
