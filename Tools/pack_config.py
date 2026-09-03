PACK_NAME = "WordHunterWoW-Dictionary-PTBR"

LOCALES = {
    "ptBR": {
        "api": "pt_BR",
        "source": "pt",
        "variable": "WordHunterWoW_Dictionary_PTBR",
        "output": "DictionaryPTBR.lua",
        "curated": "CuratedPTBR.jsonl",
        "single_char_words": "aoeéà",
        # Function words. A quest field that is thick with the English ones and
        # thin on these is an untranslated row sitting in the locale file, and
        # its words are not Portuguese words.
        "stopwords": ("o", "a", "os", "as", "um", "uma", "de", "do", "da",
                      "dos", "das", "que", "para", "com", "não", "está",
                      "este", "esta", "no", "na", "ao", "à", "você"),
    },
}

ENGLISH_STOPWORDS = ("the", "and", "you", "your", "with", "from", "that",
                     "this", "have", "will", "they", "them", "been", "must",
                     "into", "there", "their", "what", "when", "would")
