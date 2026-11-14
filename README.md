# QuestWordHunter — Brazilian Portuguese Dictionary

Learning Portuguese from quests is great until every second sentence sends you to a translator.

This is a ready-made Portuguese→English glossary built from real quest text, so the words you click already have a meaning waiting. **63,990 words.**

## Install

Unzip into the `Interface\AddOns\` folder of your game (`_retail_`, `_classic_era_` or `_forever_`) and restart the game.

You need:

- [QuestWordHunter](https://github.com/Ironship/WordHunterWoW) **1.22.6 or newer**
- Target language set to **Portuguese (Brazil)**

Words stay in the pack and are not copied into your saved data. Change any translation you like — your version wins, and **Reset to dictionary** brings this one back.

This dictionary is read only when its language is the one you are learning, so having several packs installed costs no memory for the others. QuestWordHunter loads it at login, or the moment you pick the language in its settings. A pack installed or updated while the game is running needs a restart to be noticed, and it needs QuestWordHunter 1.22.6 or newer: an older one never loads it.

## Good to know

These translations are machine-made. They will get you through a quest, but expect the odd word to be off — a name translated literally, or the wrong sense of a word that has several. Fix any of them as you go; your edit sticks.

**689 words were added on 2026-11-14** (458 ordinary words and 231 names) from a second pass over the Portuguese quest text in MultiLanguage, which found words the dictionary did not have yet. Only single words were taken; no sentence is shipped. These glosses are machine translations and have not been read through by hand, and the names are kept as they are.

**751 more words were added on 2026-11-14** from the item, spell and NPC descriptions in MultiLanguage (ordinary words such as terms of equipment and spell effects; the names of items, spells and NPCs were not taken). These glosses are machine translations too and have not been read through by hand.

The [German pack](https://github.com/Ironship/WordHunterWoW-Dictionary-DE) is the one that has been checked by hand, word by word.

## Other languages

There are packs for [French](https://github.com/Ironship/WordHunterWoW-Dictionary-FR), [Spanish](https://github.com/Ironship/WordHunterWoW-Dictionary-ES) and [Italian](https://github.com/Ironship/WordHunterWoW-Dictionary-IT) too.

Want English quest text beside the original as well? That is [English Quest Panel](https://github.com/Ironship/WordHunterWoW-ENPanel).

Retail 12.1, Classic Era and WoW Forever. GPL v3 — see `LICENSE`.

## Rebuild (maintainers)

Blizzard API keys in `Tools/keys.env`, then:

```
python Tools/fetch_quests.py
python Tools/build_wordlist.py
python Tools/translate_google.py
python Tools/build_dictionary_lua.py
```

Commit the generated `Data/DictionaryPTBR.lua`; do not commit `Data/cache/`.
