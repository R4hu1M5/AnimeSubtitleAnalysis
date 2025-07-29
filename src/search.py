from pymongo import MongoClient
import xml.etree.ElementTree as ET
from lxml import etree
import pykakasi
import re
import os

JP_CHAR_REGEX = re.compile(r'[\u3040-\u30FF\u4E00-\u9FFF]+')
kks = pykakasi.kakasi()

def find(query, lang="jp", db_name="anime", collection_name="subtitles"):
    print(f"Searching for {query} in the database")
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db[collection_name]
    # Match query text only for given language
    cursor = collection.aggregate([
        { "$unwind": "$subtitles" },
        { "$match": { f"subtitles.{lang}": { "$regex": query } } }
    ])
    print("Grouping matched subtitle instances by episode")
    matches = {}
    for doc in cursor:
        ep_id, title, sub = doc["id"], doc["title"], doc["subtitles"]
        sub_id = sub["id"]
        if ep_id not in matches:
            matches[ep_id] = {
                "title": title,
                "sub_ids": set()
            }
        matches[ep_id]["sub_ids"].add(sub_id)
    return matches

def expand(matches, lang="jp", db_name="anime", collection_name="subtitles"):
    search_radius = 2
    print(f"Expanding search radius to {search_radius} subtitle instances")
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db[collection_name]
    results = {}
    for ep_id, ep_data in matches.items():
        episode = collection.find_one({ "id": ep_id })
        title, subs = episode["title"], episode["subtitles"]
        matched_subs = []
        # Retrieve subtitle instances above/below search result to account for
        # sentence structure mismatch between EN and JP
        for sub_id in ep_data["sub_ids"]:
            i = int(sub_id) - 1
            start = max(0, i - search_radius)
            end = min(len(subs), i + search_radius + 1)
            window = subs[start:end]
            # Concatenate subtitle text in retrieved window (ignoring timestamps)
            concatenated = {
                "id": sub_id,
                lang: " ".join([s[lang] for s in window])
            }
            other_lang = "en" if lang == "jp" else "jp"
            concatenated[other_lang] = " ".join([s[other_lang] for s in window])
            matched_subs.append(concatenated)
        results[ep_id] = {
            "title": title,
            "subtitles": matched_subs
        }
    return results

def scan(db_name="anime", collection_name="subtitles"):
    search_radius = 2
    print("Scanning entire collection for untranslated words")
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db[collection_name]
    cursor = collection.find()
    results = {}
    for doc in cursor:
        ep_id, title, subs = doc["id"], doc["title"], doc["subtitles"]
        # Same logic as in expand()
        for i in range(len(subs)):
            start = max(0, i - search_radius)
            end = min(len(subs), i + search_radius + 1)
            window = subs[start:end]
            jp_text = " ".join([s["jp"] for s in window])
            en_text = " ".join([s["en"] for s in window])
            # Transliterate JP to EN and then search for common words
            jp_words = JP_CHAR_REGEX.findall(jp_text)
            romaji_candidates = set()
            for word in jp_words:
                romaji_candidates.update([item['hepburn'] for item in kks.convert(word)])
            if any(romaji in en_text.lower() for romaji in romaji_candidates):
                if ep_id not in results:
                    results[ep_id] = {
                        "title": title,
                        "subtitles": []
                    }
                results[ep_id]["subtitles"].append({
                    "id": subs[i]["id"],
                    "jp": jp_text,
                    "en": en_text
                })
    return results

def build(res, task_attrs, path):
    print("Creating XML tree for the search results")
    if "term" not in task_attrs:
        path = f"results/task{task_attrs["task"]}.xml"
    else:
        path = f"results/task{task_attrs["task"]}_term{task_attrs["term"]}.xml"
    results = ET.Element("results", attrib=task_attrs)
    for ep_id, ep_data in res.items():
        episode = ET.SubElement(results, "episode", attrib={"id": ep_id, "title": ep_data["title"]})
        for s in ep_data["subtitles"]:
            sub = ET.SubElement(episode, "subtitle", attrib={"id": s["id"]})
            ET.SubElement(sub, "dialogue", attrib={"lang": "jp"}).text = s["jp"]
            ET.SubElement(sub, "dialogue", attrib={"lang": "en"}).text = s["en"]

    print(f"Writing tree to {path}")
    print(repr(path), type(path))
    tree = ET.ElementTree(results)
    tree.write(str(path), encoding="utf-8", xml_declaration=True)

def transform(xml_path, xslt_path):
    html_path = os.path.splitext(xml_path)[0] + ".html"
    print(f"Generating {html_path}")
    xml = etree.parse(f"{xml_path}")
    xslt = etree.parse(xslt_path)
    transform = etree.XSLT(xslt)
    result = transform(xml)
    with open(html_path, "wb") as f:
        f.write(etree.tostring(result, pretty_print=True, encoding="utf-8"))
