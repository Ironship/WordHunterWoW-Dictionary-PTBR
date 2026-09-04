# QuestWordHunter — Brazilian Portuguese Dictionary

Learning Portuguese from quests is great until every second sentence sends you to a translator.

This is a ready-made Portuguese→English glossary built from real quest text, so the words you click already have a meaning waiting. **62,550 words.**

## Install

Unzip into `_retail_\Interface\AddOns\` and restart the game.

You need:

- [QuestWordHunter](https://github.com/Ironship/WordHunterWoW) **1.6.0 or newer**
- Target language set to **Portuguese (Brazil)**

Words stay in the pack and are not copied into your saved data. Change any translation you like — your version wins, and **Reset to dictionary** brings this one back.

## Good to know

These translations are machine-made. They will get you through a quest, but expect the odd word to be off — a name translated literally, or the wrong sense of a word that has several. Fix any of them as you go; your edit sticks.

The [German pack](https://github.com/Ironship/WordHunterWoW-Dictionary-DE) is the one that has been checked by hand, word by word.

## Other languages

There are packs for [French](https://github.com/Ironship/WordHunterWoW-Dictionary-FR), [Spanish](https://github.com/Ironship/WordHunterWoW-Dictionary-ES) and [Italian](https://github.com/Ironship/WordHunterWoW-Dictionary-IT) too.

Want English quest text beside the original as well? That is [English Quest Panel](https://github.com/Ironship/WordHunterWoW-ENPanel).

Retail 12.1 and Classic Era. GPL v3 — see `LICENSE`.

## Rebuild (maintainers)

Blizzard API keys in `Tools/keys.env`, then:

```
python Tools/fetch_quests.py
python Tools/build_wordlist.py
python Tools/translate_google.py
python Tools/build_dictionary_lua.py
```

Commit the generated `Data/DictionaryPTBR.lua`; do not commit `Data/cache/`.
