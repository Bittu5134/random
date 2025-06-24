import requests
import json

path = "orvcord/feed.json"
url = "https://flamecomics.xyz/_next/data/OG-uJ8nhcG8usaV_1hTQT/series/2/0c9db8012fbd1257.json"
last_chid = "2.0"
response = requests.get(url)
data = response.json()

with open(path, 'r') as f:
    chid = json.load(f)["chid"]

series_detail = data['pageProps']['chapterList']
data = []

for chapter_element in series_detail:
    chapter_info = {
"chapter": chapter_element['chapter'],
"Id": chapter_element['chapter_id'],
"token": chapter_element['token'],
"title": chapter_element['title'],

"release_date": chapter_element['release_date']
}
    #print(chapter_info)
    if chid == chapter_element['chapter']:
        print(chapter_info, last_chid)
        data.append(chapter_info)
        break
    else:
        chid_last = chapter_element['chapter']
with open(path, 'w') as f:
    json.dump({"chid":chid_last,"data":data}, f, indent=4)
