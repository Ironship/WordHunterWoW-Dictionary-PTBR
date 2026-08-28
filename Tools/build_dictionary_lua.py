#!/usr/bin/env python3
import argparse, json, pathlib
from pack_config import LOCALES

ROOT = pathlib.Path(__file__).resolve().parents[1]

def quote(value):
    return '"' + str(value or "").replace('\\', '\\\\').replace('"', '\\"').replace('\r', '').replace('\n', '\\n') + '"'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", choices=LOCALES, default=next(iter(LOCALES)))
    args = parser.parse_args()
    config = LOCALES[args.locale]
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
            if record.get("translation"): records[record["key"]] = record
    lines = [f"{config['variable']} = {config['variable']} or {{}}"]
    for key in sorted(records):
        record = records[key]
        lines.append(f"{config['variable']}[{quote(key)}] = {{ word = {quote(record['word'])}, translation = {quote(record['translation'])}, note = {quote(record.get('note'))} }}")
    target = ROOT / "Data" / config["output"]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"locale={args.locale} entries={len(records)} output={target}")

if __name__ == "__main__": main()
