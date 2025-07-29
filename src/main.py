from vars import LANGUAGES, TITLES
from parse import parse, align, write
from insert import parse_xml, insert
from search import find, expand, scan, build, transform
import os

# Task 1: Examine translation of titles such as 先生 (sensei) and honorifics such as さん (-san)
# Task 2: Compute percentage of words left untranslated
# Task 3: Examine variations in translation of standard phrases such as よろしく (yoroshiku)
search_terms = {
    1: ["先生", "先輩", r"[一-龯]さん", r"[一-龯]くん"], # Regex to avoid false positives
    3: ["よろしく", "いただきます"]
}

def create(name, ep):
    pwd = os.path.dirname(os.path.abspath(__file__))
    subs = []
    for lang in LANGUAGES:
        parse_path = os.path.join(pwd, "..", "subtitles", name, f"{ep:02d}.{lang}.srt")
        subs.append(parse(parse_path))
    en_subs, jp_subs = subs
    aligned_subs = align(en_subs, jp_subs)
    xml_path = os.path.join(pwd, "..", "subtitles_xml", name, f"{ep:02d}.xml")
    attrs = { "name": name, "episode": ep }
    write(aligned_subs, xml_path, attrs)
    data = parse_xml(xml_path)
    insert(data, LANGUAGES)

def search():
    pwd = os.path.dirname(os.path.abspath(__file__))
    xslt_path = os.path.join(pwd, "..", "results", "transform.xslt")
    for task in range(1, 4):
        # Task 2
        if task == 2:
            results = scan()
            task_attrs = { "task": str(task), "key": "Untranslated Words" }
            xml_path = os.path.join(pwd, "..", "results", f"task{task}.xml")
            build(results, task_attrs, xml_path)
            transform(xml_path, xslt_path)
        # Task 1&3
        else:
            for i, term in enumerate(search_terms[task], start=1):
                matches = find(term)
                results = expand(matches)
                task_attrs = { "task": str(task), "term": str(i), "key": term }
                xml_path = os.path.join(pwd, "..", "results", f"task{task}_term{i}.xml")
                build(results, task_attrs, xml_path)
                transform(xml_path, xslt_path)

if __name__ == "__main__":
    for title in TITLES:
        for episode in range(1, title["episodes"]+1):
            create(title["name"], episode)
    search()