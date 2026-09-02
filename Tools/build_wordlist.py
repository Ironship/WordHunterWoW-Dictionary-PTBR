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
    # Single letters are almost always initials or list markers, but a handful are real
    # words in these languages (Italian "e", "i", "è"; French "à", "y"). Keep only those.
    singles = set(LOCALES[args.locale].get("single_char_words", ""))
    source = ROOT / f"Data/cache/quests_{args.locale}.jsonl"
    for line in source.read_text(encoding="utf-8").splitlines():
        quest = json.loads(line)
        # progress and reward only ever arrive via import_harvest.py -- the quest
        # API publishes neither, and objectives comes back empty from it too.
        for field in ("title", "description", "objectives", "progress", "completion", "reward"):
            text = quest.get(field) or ""
            for word in TOKEN.findall(text):
                key = word.casefold()
                if len(key) < 2 and key not in singles: continue
                counts[key] += 1
                forms[key][word] += 1
                contexts.setdefault(key, text[:500])
    target = ROOT / f"Data/cache/wordlist_{args.locale}.jsonl"
    with target.open("w", encoding="utf-8") as output:
        for key in sorted(counts):
            output.write(json.dumps({"key": key, "word": forms[key].most_common(1)[0][0], "count": counts[key], "context": contexts[key]}, ensure_ascii=False) + "\n")
    print(f"words={len(counts)} output={target}")

if __name__ == "__main__": main()
