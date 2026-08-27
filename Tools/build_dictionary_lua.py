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
    source = ROOT / f"Data/cache/translations_{args.locale}_en.jsonl"
    records = {}
    for line in source.read_text(encoding="utf-8").splitlines():
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
