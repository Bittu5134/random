
import requests
import json
from datetime import datetime
from pprint import pprint

path = "orvcord/feed.json"
webhook = os.environ("WEBHOOK")
url = "https://flamecomics.xyz/series/2"
last_chid = "2.0"
theme = 1581906

async def get_and_print_target_url(url: str, duration: int):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        found_url_container = [None]

        async def _route_handler(route):
            if route.request.resource_type == "image":
                await route.abort()
            else:
                if "/series/2/" in route.request.url and found_url_container[0] is None:
                    found_url_container[0] = route.request.url
                await route.continue_()

        await page.route("**/*", _route_handler)

        await page.goto(url)
        await asyncio.sleep(duration)
        await browser.close()

        if found_url_container[0]:
            print(f"Found URL: {found_url_container[0]}")
            return found_url_container[0]
        else:
            print("No matching URL found.")

capture_duration = 5
url = await get_and_print_target_url(url, capture_duration)


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
  "content": "||*meow*||",
  "embeds": [
    {
      "title": f"✨ Chapter {chapter_element['chapter'].replace('.0','')} - {chapter_element['title']}",
      "description": "> ### Head over to Webtoon and catch up with the chaos, drama, and brilliance of ORV",
      "color": theme,
      "image": {
        "url": cover
      },
      "fields": [
        {
          "name": f"🏮 **Chapter**: {chapter_element['chapter'].replace('.0','')}",
          "value": " "
        },
        {
          "value": " ",
          "name": f"🗓️ **Release Date**"
        },
        {
          "name": f"<t:{chapter_element['release_date']}:F>",
          "value": " "
        },
        {
          "name": "📖 Read on Webtoon",
          "value": f"**[click to visit ↗](https://www.webtoons.com/en/action/omniscient-reader/list?title_no=2154)**"
        },
        {
          "name": "",
          "value": "**━━━━━━━━━━━━━━━━━━━━━━━━━━━**"
        },
        {
          "name":"💬 Discussions",
          "value": "<#1323975536707637299>\n\n```\n- Do not discuss or send Fast pass chapters to this channel.\n- Watch ads to unlock 3 extra chapters.\n```"
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
    json.dump({"chid":chid_last,"data":series_detail, "cover":cover, "theme": 1581906}, f, indent=4)
