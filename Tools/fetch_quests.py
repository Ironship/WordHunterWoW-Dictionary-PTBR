#!/usr/bin/env python3
import argparse, base64, csv, json, pathlib, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pack_config import LOCALES, PACK_NAME

ROOT = pathlib.Path(__file__).resolve().parents[1]

def credentials():
    values = {}
    for line in (ROOT / "Tools/keys.env").read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values["BLIZZARD_CLIENT_ID"], values["BLIZZARD_CLIENT_SECRET"]

def get_token():
    client_id, secret = credentials()
    auth = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
    request = urllib.request.Request("https://oauth.battle.net/token", data=b"grant_type=client_credentials", headers={"Authorization": f"Basic {auth}"})
    return json.load(urllib.request.urlopen(request, timeout=30))["access_token"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", choices=LOCALES, default=next(iter(LOCALES)))
    parser.add_argument("--csv", default=str(ROOT / "Data/QuestV2.csv"))
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--interval", type=float, default=0.25)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    locale = LOCALES[args.locale]
    cache = ROOT / f"Data/cache/quests_{args.locale}.jsonl"
    failed = ROOT / f"Data/cache/failed_{args.locale}.txt"
    errors = ROOT / f"Data/cache/errors_{args.locale}.jsonl"
    cache.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    for path, is_json in ((cache, True), (failed, False)):
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                try: done.add(int(json.loads(line)["id"] if is_json else line))
                except Exception: pass
    with open(args.csv, newline="", encoding="utf-8-sig") as handle:
        ids = [int(row["ID"]) for row in csv.DictReader(handle) if row.get("ID")]
    ids = [quest_id for quest_id in ids if quest_id not in done]
    if args.limit: ids = ids[:args.limit]
    token = get_token()
    write_lock, rate_lock = threading.Lock(), threading.Lock()
    next_start, processed = [0.0], [0]

    def throttle():
        with rate_lock:
            delay = max(0, next_start[0] - time.monotonic())
            if delay: time.sleep(delay)
            next_start[0] = time.monotonic() + args.interval

    def fetch(quest_id):
        url = f"https://eu.api.blizzard.com/data/wow/quest/{quest_id}?namespace=static-eu&locale={locale['api']}"
        last_error = None
        for attempt in range(5):
            throttle()
            try:
                request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": f"{PACK_NAME}/0.1"})
                data = json.load(urllib.request.urlopen(request, timeout=30))
                objectives = data.get("objectives", "")
                if isinstance(objectives, dict): objectives = objectives.get("description", "")
                record = {"id": quest_id, "title": data.get("title") or "", "description": data.get("description") or "", "objectives": objectives or ""}
                with write_lock, cache.open("a", encoding="utf-8") as output:
                    output.write(json.dumps(record, ensure_ascii=False) + "\n")
                last_error = None
                break
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    with write_lock, failed.open("a", encoding="utf-8") as output: output.write(f"{quest_id}\n")
                    last_error = None
                    break
                last_error = f"HTTP {error.code}"
                if error.code in (429, 500, 502, 503, 504): time.sleep(2 ** attempt); continue
                break
            except Exception as error:
                last_error = str(error)
                time.sleep(2 ** attempt)
        if last_error:
            with write_lock, errors.open("a", encoding="utf-8") as output:
                output.write(json.dumps({"id": quest_id, "error": last_error}, ensure_ascii=False) + "\n")
        with write_lock:
            processed[0] += 1
            if processed[0] % 500 == 0: print(f"processed={processed[0]} remaining={len(ids) - processed[0]}", flush=True)

    print(f"locale={args.locale} total={len(ids)} cached={len(done)}", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool: list(pool.map(fetch, ids))
    print("done", flush=True)

if __name__ == "__main__": main()
