import requests
import json
from datetime import datetime

path = "orvcord/feed.json"
webhook = "https://discord.com/api/webhooks/1387003307066916946/f-HmMpXXhPUMd5rura0mXtQ6SQ4y4JTQD4mGSfPdDUOSsqoA1rfdZnV_4El2-iJqqYcn"
url = "https://flamecomics.xyz/_next/data/OG-uJ8nhcG8usaV_1hTQT/series/2/0c9db8012fbd1257.json"
last_chid = "2.0"
theme = 1581906
response = requests.get(url)
data = response.json()
with open(path, 'r') as f:
    file_content = f.read() # Read the content once
    print(file_content)
    file_data = json.loads(file_content) # Load JSON from the read content
    chid = file_data["chid"]
    cover = file_data["cover"]
    theme = file_data["theme"]

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

        payload = {
  "content": "||<@&1255148096430673940>||",
  "embeds": [
    {
      "title": f"Chapter - {chapter_element['chapter'].replace('.0','')}: \n{chapter_element['title']}",
      "description": "> Head over to Webtoon and catch up with the chaos, drama, and brilliance of ORV! \n> Chapter discussions in <#1323975536707637299>. \n> Watch ads to unlock 3 extra chapters.",
      "color": theme,
      "image": {
        "url": cover
      },
      "fields": [
        {
          "name": f"📖 **Chapter**: {chapter_element['chapter'].replace('.0','')}",
          "value": " "
        },
        {
          "value": f"<t:{chapter_element['release_date']}:D>",
          "name": f"🗓️ **Release Date**"
        },
        {
          "name": " ",
          "value": f"🌐 **[Read on Webtoon ↗](https://www.webtoons.com/en/action/omniscient-reader/list?title_no=2154)**"
        },
      ],
     "thumbnail": {
        "url": f"https://cdn.flamecomics.xyz/series/2/{chapter_element['token']}/cover.png"
      },
      "footer": {
        "text": "Posted by Cute Cats"
      },
      "timestamp": datetime.utcnow().isoformat(),
    },
  ],
  "attachments": []
}

        headers = {"Content-Type": "application/json"}
        requests.post(webhook, data=json.dumps(payload), headers=headers)

        break
    else:
        chid_last = chapter_element['chapter']
with open(path, 'w') as f:
    json.dump({"chid":chid_last,"data":data, "cover":cover, "theme": 1581906}, f, indent=4)
