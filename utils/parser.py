import requests
import bs4
import json


def parse_page(song_link):
    headers = {"Content-type": "application/json"}
    raw_song = requests.get(song_link, headers=headers).content
    soup = bs4.BeautifulSoup(raw_song, "html.parser")
    script = soup.find_all('script')[5].text.strip()[20:]
    data = json.loads(script)

    return data
