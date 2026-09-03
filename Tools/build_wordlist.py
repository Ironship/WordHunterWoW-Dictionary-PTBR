#!/usr/bin/env python3
import argparse, collections, json, pathlib, re
from pack_config import LOCALES, ENGLISH_STOPWORDS

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*", re.UNICODE)

# The English text of the same quests. A field that is byte-identical to it was
# never translated -- the row is English sitting in a locale file -- and its
# words are not words of this language. Left in, they take over the top of the
# uncurated list: an audit wave came back 90% English function words ("at", "my",
# "the"), because every real Italian word above them had already been done.
ENGLISH = pathlib.Path(__file__).resolve().parents[2] / \
    "WordHunterWoW-ENPanel/Data/cache/quests_enUS.jsonl"


def english_by_id(path):
    rows = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                quest = json.loads(line)
            except Exception:
                continue
            rows[str(quest.get("id"))] = quest
    return rows


def untranslated(text, reference):
    """Is this field the English text rather than the locale's own?

    Not always byte-identical: an untranslated row often carries the English
    paragraph with a line of locale boilerplate appended after it -- quest 5
    holds the English description followed by "Al completamento di questa
    missione otterrai:". So containment counts, guarded by two conditions that
    keep a short English fragment inside real Italian prose from tripping it:
    the reference has to be long enough to mean something, and it has to make up
    most of the field.
    """
    text = (text or "").strip()
    reference = (reference or "").strip()
    if not text or not reference:
        return False
    if text == reference:
        return True
    return (len(reference) >= 12 and reference in text
            and len(reference) >= 0.6 * len(text))


def reads_as_english(words, native):
    """Second test, for rows our English copy does not cover.

    Comparing against the English text only catches a row we happen to hold in
    English too. The rest are caught by what the words themselves are: real
    Italian prose of any length carries di, il, che, per; English prose carries
    the, and, you, with. The margin is deliberately wide -- three or more
    English function words and more than twice as many as Italian ones -- so a
    quest that quotes an English name in an Italian sentence is left alone.
    """
    if len(words) < 8:
        return False
    english = sum(1 for w in words if w in ENGLISH_STOPWORDS)
    home = sum(1 for w in words if w in native)
    return english >= 3 and english > 2 * home


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", choices=LOCALES, default=next(iter(LOCALES)))
    parser.add_argument("--english", default=str(ENGLISH),
                        help="quest text in English; fields identical to it are skipped")
    parser.add_argument("--keep-english", action="store_true",
                        help="do not skip untranslated fields (for comparison)")
    args = parser.parse_args()
    english = {} if args.keep_english else english_by_id(pathlib.Path(args.english))
    skipped = 0
    counts, forms, contexts = collections.Counter(), collections.defaultdict(collections.Counter), {}
    # Single letters are almost always initials or list markers, but a handful are real
    # words in these languages (Italian "e", "i", "è"; French "à", "y"). Keep only those.
    singles = set(LOCALES[args.locale].get("single_char_words", ""))
    native = set(LOCALES[args.locale].get("stopwords", ()))
    source = ROOT / f"Data/cache/quests_{args.locale}.jsonl"
    for line in source.read_text(encoding="utf-8").splitlines():
        quest = json.loads(line)
        # progress and reward only ever arrive via import_harvest.py -- the quest
        # API publishes neither, and objectives comes back empty from it too.
        reference = english.get(str(quest.get("id")), {})
        for field in ("title", "description", "objectives", "progress", "completion", "reward"):
            text = quest.get(field) or ""
            if untranslated(text, reference.get(field)):
                skipped += 1
                continue
            tokens = TOKEN.findall(text)
            if not args.keep_english and reads_as_english(
                    [t.casefold() for t in tokens], native):
                skipped += 1
                continue
            for word in tokens:
                key = word.casefold()
                if len(key) < 2 and key not in singles: continue
                counts[key] += 1
                forms[key][word] += 1
                contexts.setdefault(key, text[:500])
    target = ROOT / f"Data/cache/wordlist_{args.locale}.jsonl"
    with target.open("w", encoding="utf-8") as output:
        for key in sorted(counts):
            output.write(json.dumps({"key": key, "word": forms[key].most_common(1)[0][0], "count": counts[key], "context": contexts[key]}, ensure_ascii=False) + "\n")
    print(f"words={len(counts)} untranslated_fields_skipped={skipped} output={target}")

if __name__ == "__main__": main()
