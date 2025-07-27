from vars import LANGUAGES, TITLES
from parse import parse, align, write
from insert import parse_xml, insert
from search import find, expand, scan, build, transform

# Task 1: Examine translation of titles such as 先生 (sensei) and honorifics such as さん (-san)
# Task 2: Compute percentage of words left untranslated
# Task 3: Examine variations in translation of standard phrases such as よろしく (yoroshiku)
search_terms = {
    1: ["先生", "先輩", r"[一-龯]さん", r"[一-龯]くん"], # Regex to avoid false positives
    3: ["よろしく", "いただきます"]
}

def create(name, ep):
    en_subs, jp_subs = [parse(name, ep, l) for l in LANGUAGES]
    aligned_subs = align(en_subs, jp_subs)
    write(aligned_subs, name, ep)
    data = parse_xml(name, ep)
    insert(data, LANGUAGES)

def search():
    for task in range(1, 4):
        # Task 2
        if task == 2:
            results = scan()
            build(results, task)
            transform(task)
        # Task 1&3
        else:
            for i, term in enumerate(search_terms[task], start=1):
                matches = find(term)
                results = expand(matches)
                build(results, (task, i, term), has_terms=True)
                transform((task, i), has_terms=True)

if __name__ == "__main__":
    for title in TITLES:
        for episode in range(1, title["episodes"]+1):
            create(title["name"], episode)
    search()