import xml.etree.ElementTree as ET
from pymongo import MongoClient

def parse_xml(name, ep):
    path = f"../subtitles_xml/{name}/{ep:02d}.xml"
    print(f"Reading {path}")
    episode = ET.parse(path).getroot()
    id = episode.attrib.get("id")
    title = episode.attrib.get("title")
    subs = []
    # Retrieve element text using inbuilt functions and XPath '@' notation
    for sub in episode.findall("subtitle"):
        entry = {
            "id": sub.attrib.get("id"),
            "start": sub.findtext("start"),
            "end": sub.findtext("end"),
            "jp": sub.find("dialogue[@lang='jp']").text,
            "en": sub.find("dialogue[@lang='en']").text,
        }
        subs.append(entry)

    # Build data in format to be inserted into database
    return {
        "id": id,
        "title": title,
        "subtitles": subs
    }

def insert(data, langs, db_name="anime", collection_name="subtitles"):
    print(f"Inserting data into database '{db_name}', collection '{collection_name}'")
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db[collection_name]
    # Replace entry if it already exists (in case of repeated runs) else insert
    existing = collection.find_one({"id": data["id"]})
    if existing:
        collection.replace_one({"id": data["id"]}, data)
    else:
        collection.insert_one(data)
    # Create indices for episode ID and subtitle text itself for full-text search
    collection.create_index("id", unique=True)
    sub_indices = [(f"subtitles.{l}", "text") for l in langs]
    collection.create_index(sub_indices)