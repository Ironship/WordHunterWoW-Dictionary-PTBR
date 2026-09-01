# Brazilian Portuguese dictionary audit — instructions

You are improving a Portuguese→English dictionary used by a World of Warcraft
addon. Players read Brazilian Portuguese quest text and click a word to see its
English meaning plus a short note. Your job is to fix machine-translation errors
and write notes that teach the reader something worth knowing.

## Input

`Data/cache/audit_work/in/batch_NN.jsonl` — one JSON object per line:

- `key` — lowercase lookup key. **Copy it through byte for byte.** It is already
  casefolded the way the addon looks words up, and accents and the cedilla are
  part of the key: `você`, `não`, `coração`, `açúcar` keep theirs. Do not
  ASCII-fold `á â ã à é ê í ó ô õ ú ç`, do not re-case, and above all do not add
  an accent the key does not have — `e` and `é` are different words with
  different keys, and "correcting" one into the other silently overwrites the
  wrong entry. Copy the key and the word exactly as given: a changed key breaks
  the lookup, and a changed word breaks the repair path that would otherwise
  recover it.
- `word` — the Portuguese word as it appears in game. **Copy through verbatim.**
- `current` — the existing Google Translate output. Often right, sometimes wrong.
- `count` — how often the word occurs across all quests.
- `context` — a real quest sentence containing the word.

## Output

`Data/cache/audit_work/out/batch_NN.jsonl` — one JSON object per input line,
**same order, same count, same keys**, with exactly these four fields:

```json
{"key":"ventobravo","word":"Ventobravo","translation":"Stormwind","note":"vento (wind) + bravo (fierce); the human capital"}
```

Write the file with the Write tool, in one single write. Do not use apply_patch:
a file of 150 dense JSON lines is not a patchable target and the attempt fails.
UTF-8, no BOM, no trailing commas, no markdown fences, one compact JSON object
per line.

## Do both jobs in one pass

The two halves of this task are the translation and the note, and they carry
equal weight. Agents on this task reliably do one and skip the other: a pass
told to care about notes stops touching translations, and a pass told to care
about translations writes four notes in a hundred and fifty rows.

A healthy pass revises a good share of the translations and leaves a note on
nearly every row that is owed one. A bare proper name is not owed a note, and an
empty one is correct there — you must not invent lore.

**Do not append a synonym to a translation that is already correct.** Repeating
the existing answer unchanged is the right outcome when it is right; padding it
out to look busy is not a correction and is easy to spot.

## Errors to look for before you accept `current`

Google is right often enough that skimming feels safe. These are the mistakes it
actually makes on Portuguese quest text:

- an accent dropped or added, which changes the word entirely: `e` is "and",
  `é` is "is"; `a` is "the", `à` is "to the"; `esta` is "this", `está` is "is";
  `por` is "by", `pôr` is "to put"; `sabia` is "knew", `sábia` is "wise"
- the subjunctive read as an indicative (`tenha` is "may have", not "has"), and
  the personal infinitive missed entirely (`para vermos` is "for us to see")
- a preterite flattened to a present (`levou` is "took", not "takes")
- an imperative read as a third person (`colete` as a command is "collect" —
  quest objectives are commands)
- a false friend taken at face value: `pretender` is to intend not to pretend,
  `puxar` is to pull not to push, `livraria` is a bookshop not a library,
  `parentes` are relatives not parents, `assistir` is to watch not to assist,
  `realizar` is to carry out not to realise, `esquisito` is strange not exquisite
- the two verbs "to be" collapsed into one English "to be" with no hint whether
  it is `ser` or `estar`
- a plural rendered as a singular, or the reverse — `-ão` plurals (`mão`/`mãos`,
  `pão`/`pães`, `coração`/`corações`) are irregular and easy to miss
- an official English WoW name missed, or invented

## translation

- Give the meaning that fits **WoW quest text**, not a dictionary's first entry.
- Use the **official English WoW term** when the Portuguese is a game proper
  noun, and only when you are confident of it. If you are not, give a clean
  literal translation instead. **Do not invent lore, zone names, or NPC names.**
  This is the single most damaging mistake available here: in the Spanish pack a
  coined place name had been glossed "Ironforge" and was in fact Razor Hill.
- Separate genuinely distinct senses with `; ` — at most three, most common first.
- Keep the grammatical category of the Portuguese word (noun → noun, verb → verb).
  Nouns: no article. Verbs: bare infinitive without "to" unless it disambiguates.
- Capitalise by English convention, not the source's. Portuguese lowercases
  things English capitalises — `português` → Portuguese, `terça-feira` →
  Tuesday, `janeiro` → January — so the translation is capitalised even though
  the word is not.
- If `current` is already the best answer, repeat it unchanged. That is a normal
  and expected outcome.

## note

This is the part the reader actually reads for pleasure. Make it earn its place.

1. **Word breakdown**, when it illuminates the word:
   `escuridão` → "escuro (dark) + -idão, the suffix that turns adjectives into nouns"
2. **False friend / trap**, when a learner would guess wrong:
   `pretender` → "false friend: means to intend, never to pretend"
3. **Official name differs from the literal sense**, when you are sure of it
4. **Idiom or fixed phrase** the word usually appears in:
   `dar` → "dar conta de = to manage, to cope with"
5. **Etymology or a genuinely interesting fact**:
   `almoço` → "from Latin admordium, a first bite"

Rules:

- English, lowercase start, **no trailing period**, at most ~120 characters.
- Never merely restate the translation ("means darkness") — that is wasted space.
- Never write filler like "common verb" or "common Portuguese word" on its own.
- If nothing worth saying comes to mind, use `""`. An empty note is much better
  than a boring one, and it is the right answer for a bare proper name.
- Where Brazilian and European usage genuinely differ, the note is the place to
  say so — this pack is the Brazilian one.
- No newlines, no quotes-inside-quotes problems — keep it plain.

## Accuracy

Getting a translation wrong is worse than leaving it as it was. When torn between
a confident literal reading and a half-remembered WoW term, choose the literal
one and say in the note what you could not confirm. Do not guess at lore.
