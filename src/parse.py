import re
from datetime import timedelta
import xml.etree.ElementTree as ET


def parse(name, ep, lang):
    path = f"../subtitles/{name}/{ep:02d}.{lang}.srt"
    print(f"Reading {path}")
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    print("Extracting subtitles")
    entries = re.split(r"\n\s*\n", text.strip())
    subs = []
    for entry in entries:
        lines = entry.splitlines()
        timestamps = []
        # Extract timestamp given the format "hh:mm:ss,ms --> hh:mm:ss,ms"
        for t in lines[1].split(" --> "):
            h, m, s_ms = t.split(":")
            s, ms = s_ms.split(",")
            timestamps.append(timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms)))
        start, end = timestamps
        # Merge all subtitle text lines
        sub = " ".join(lines[2:])
        subs.append({
            "start": start,
            "end": end,
            "text": sub.strip()
        })
    return subs

def align(en_subs, jp_subs, max_offset=timedelta(seconds=3)):
    print("Aligning EN and JP subtitles")
    alignment = []
    # Use a set to track which JP subtitles have already been matched
    used = set()
    for curr in en_subs:
        # Find the closest JP start time to the EN start time within the maximum subtitle offset
        candidates = [e for i, e in enumerate(jp_subs) if i not in used]
        closest = None
        min_diff = max_offset
        for c in candidates:
            diff = abs(curr["start"] - c["start"])
            if diff <= min_diff:
                min_diff = diff
                closest = c
        if closest:
            alignment.append((curr, closest))
            used.add(jp_subs.index(closest))
    return alignment

def write(aligned_subs, name, ep):
    print("Creating XML tree for the aligned subtitles")
    episode = ET.Element("episode", id=f"{name}_{ep:02d}")
    episode.set("title", f"{name.replace('_', ' ').title()} Episode {ep:02d}")
    for i, (en, jp) in enumerate(aligned_subs, start=1):
        # Create sub-elements to the root episode element following the schema
        sub = ET.SubElement(episode, "subtitle", attrib={"id": str(i)})
        ET.SubElement(sub, "start").text = str(en["start"])
        ET.SubElement(sub, "end").text = str(en["end"])
        ET.SubElement(sub, "dialogue", attrib={"lang": "en"}).text = en["text"]
        ET.SubElement(sub, "dialogue", attrib={"lang": "jp"}).text = jp["text"]
    
    path = f"../subtitles_xml/{name}/{ep:02d}.xml"
    print(f"Writing tree to {path}")
    tree = ET.ElementTree(episode)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)
