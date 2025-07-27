from vars import API_KEY, LANGUAGES, TITLES
import requests
import time

HEADERS = {
    "Accept": "*/*",
    "Api-Key": API_KEY,
    "User-Agent": "AnimeSubtitleAnalysis v1.0",
    "Content-Type": "application/json",
}

def search(name, episode, lang):
    print(f"Searching for {lang.upper()} subtitles for {name} Episode {episode:02d}")
    # Send search request
    response = requests.get(
        "https://api.opensubtitles.com/api/v1/subtitles",
        headers=HEADERS,
        params={
            "query": name,
            "LANGUAGES": lang,
            "order_by": "download_count",
            "type": "episode",
            "season_number": 1,
            "episode_number": episode,
            "limit": 1,
        },
    )
    response.raise_for_status()
    data = response.json()["data"]
    return data[0] if data else None

def download(file_id, filename):
    print(f"Downloading subtitles into {filename}")
    # Get download link for file using file_id
    response = requests.get(
        "https://api.opensubtitles.com/api/v1/download",
        headers=HEADERS,
        params={"file_id": file_id},
    )
    response.raise_for_status()
    download_link = response.json().get("link")
    if not download_link:
        print("No download link found")
        return
    # Send download request
    response = requests.get(download_link)
    response.raise_for_status()
    with open(filename, "wb") as f:
        f.write(response.content)

def collect():
    for title in TITLES:
        for episode in range(1, title["episodes"]+1):
            for lang in LANGUAGES:
                name = title["name"].replace('_', ' ').title()
                res = search(name, episode, lang)
                if not res:
                    print("No subtitles found")
                    continue
                files = res["attributes"].get("files")
                if not files or "file_id" not in files[0]:
                    print("No downloadable file available")
                    continue
                file_id = files[0]["file_id"]
                filename = f"../subtitles/{title["name"]}/{episode:02d}.{lang}.srt"
                download(file_id, filename)
                # Avoid overloading the API
                time.sleep(1)

if __name__ == "__main__":
    collect()
