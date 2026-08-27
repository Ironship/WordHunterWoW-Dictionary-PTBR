#!/usr/bin/env python3
import argparse, collections, json, pathlib, re
from pack_config import LOCALES

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*", re.UNICODE)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", choices=LOCALES, default=next(iter(LOCALES)))
    args = parser.parse_args()
    counts, forms, contexts = collections.Counter(), collections.defaultdict(collections.Counter), {}
    source = ROOT / f"Data/cache/quests_{args.locale}.jsonl"
    for line in source.read_text(encoding="utf-8").splitlines():
        quest = json.loads(line)
        for text in (quest.get("title") or "", quest.get("description") or "", quest.get("objectives") or ""):
            for word in TOKEN.findall(text):
                if len(word) < 2: continue
                key = word.casefold()
                counts[key] += 1
                forms[key][word] += 1
                contexts.setdefault(key, text[:500])
    target = ROOT / f"Data/cache/wordlist_{args.locale}.jsonl"
    with target.open("w", encoding="utf-8") as output:
        for key in sorted(counts):
            output.write(json.dumps({"key": key, "word": forms[key].most_common(1)[0][0], "count": counts[key], "context": contexts[key]}, ensure_ascii=False) + "\n")
    print(f"words={len(counts)} output={target}")

if __name__ == "__main__": main()
