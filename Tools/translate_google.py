#!/usr/bin/env python3
import argparse, json, pathlib, threading, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pack_config import LOCALES

ROOT = pathlib.Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", choices=LOCALES, default=next(iter(LOCALES)))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--interval", type=float, default=0.25)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    source_lang = LOCALES[args.locale]["source"]
    wordlist = ROOT / f"Data/cache/wordlist_{args.locale}.jsonl"
    target = ROOT / f"Data/cache/translations_{args.locale}_en.jsonl"
    errors = ROOT / f"Data/cache/translation_errors_{args.locale}.jsonl"
    done = {}
    if target.exists():
        for line in target.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
                if record.get("translation"): done[record["key"]] = record
            except Exception: pass
    records = [json.loads(line) for line in wordlist.read_text(encoding="utf-8").splitlines()]
    records = [record for record in records if record["key"] not in done]
    if args.limit: records = records[:args.limit]
    target.parent.mkdir(parents=True, exist_ok=True)
    lock, rate_lock = threading.Lock(), threading.Lock()
    next_start, processed = [0.0], [0]

    def throttle():
        with rate_lock:
            delay = max(0, next_start[0] - time.monotonic())
            if delay: time.sleep(delay)
            next_start[0] = time.monotonic() + args.interval

    def translate(record):
        translation, last_error = "", None
        for attempt in range(4):
            throttle()
            params = urllib.parse.urlencode({"client": "dict-chrome-ex", "sl": source_lang, "tl": "en", "q": record["word"]})
            try:
                request = urllib.request.Request("https://clients5.google.com/translate_a/t?" + params, headers={"User-Agent": "Mozilla/5.0"})
                data = json.load(urllib.request.urlopen(request, timeout=20))
                if isinstance(data, str): translation = data.strip()
                elif isinstance(data, list) and data and isinstance(data[0], str): translation = data[0].strip()
                if translation: break
                last_error = "empty translation"
            except Exception as error:
                last_error = str(error)
            time.sleep(2 ** attempt)
        if translation:
            result = {**record, "translation": translation, "note": ""}
            with lock, target.open("a", encoding="utf-8") as output: output.write(json.dumps(result, ensure_ascii=False) + "\n")
        else:
            with lock, errors.open("a", encoding="utf-8") as output: output.write(json.dumps({"key": record["key"], "error": last_error}, ensure_ascii=False) + "\n")
        with lock:
            processed[0] += 1
            if processed[0] % 500 == 0: print(f"processed={processed[0]} remaining={len(records) - processed[0]}", flush=True)

    print(f"locale={args.locale} to_translate={len(records)} cached={len(done)}", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool: list(pool.map(translate, records))
    print("done", flush=True)

if __name__ == "__main__": main()
