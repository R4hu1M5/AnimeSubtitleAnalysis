# AnimeSubtitleAnalysis

## Overview

**AnimeSubtitleAnalysis** has been developed to analyze a parallel corpus of English and Japanese subtitles for anime series. It is capable of performing the following tasks:

### Task 1: Translation of Titles and Honorifics
Analyzing the variations in translation of titles such as `先生 (sensei)` and `先輩 (senpai)` and honorifics such as `さん (-san)` and `くん (-kun)`.

###  Task 2: Untranslated Words
Analyzing instances where Japanese words have simply been transliterated into English, whether it be due to a localization preference or a lack of a good translation alternative. This task is conceptually incomplete, since it does not exclude proper nouns, which would obviously be left untranslated.

### Task 3: Translation of Standard Phrases
Analyzing the variations in translation of standard phrases such as `よろしく (yoroshiku)` and `いただきます (itadakimasu)` which are translated differently across usage instances due to the lack of a cultural equivalent.

---

## How to Run

Create an API key on [OpenSubtitles](https://www.opensubtitles.com), add it to `src/vars.py` and run the following command to download the required subtitles:

```bash
python3 src/collect.py
```

Set up MongoDB on local and run the following command:

```bash
python3 src/main.py
```