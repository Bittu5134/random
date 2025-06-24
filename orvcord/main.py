import requests
import xml.etree.ElementTree as ET
import os
import json
import re # Import the re module for regular expressions

# Replace 'YOUR_WEBHOOK_URL' with your actual Discord webhook URL
# WEBHOOK_URL = 'https://discord.com/api/webhooks/1387003307066916946/f-HmMpXXhPUMd5rura0mXtQ6SQ4y4JTQD4mGSfPdDUOSsqoA1rfdZnV_4El2-iJqqYcn'
WEBHOOK_URL = os.environ.get('WEBHOOK')

# Check if the webhook URL is set
if not WEBHOOK_URL:
    print("Error: WEBHOOK_URL environment variable not set. Please set it before running the script.")
    exit(1)


# The JSON payload you want to send
DISCORD_MESSAGE_PAYLOAD = {
  "username": "ORV News",
  "embeds": [
    {
      "author": {
        "name": "✨ ORV 260: The Story Continues.."
      },
      "title": "> Chapter 260 is here!\n> The tension rises and new > twists await—dive into the chaos of the next scenario with Kim Dokja and the companions.\n> Catch up now on Webtoon > before spoilers find you!",
      "color": 4810725,
      "fields": [
        {
          "name": "📖 Chapter",
          "value": "Episode 260 – Omniscient Reader's Viewpoint"
        },
        {
          "name": "📅 Released On",
          "value": "June 24, 2025"
        },
        {
          "name": "🔗 Read Now",
          "value": "[Click here to read on Webtoon](https://m.webtoons.com/en/action/omniscient-reader/episode-260/viewer?title_no=2154&episode_no=261)"
        },
        {
          "name": "⚠️ Spoiler Warning",
          "value": "Please use <#1323975536707637299> for discussions and tag spoilers properly."
        }
      ],
      "image": {
        "url": "https://cdn.discordapp.com/attachments/1385770814682562581/1386983519741280287/Picsart_25-06-24_13-47-06-992.jpg?ex=685bb090&is=685a5f10&hm=af4587b8b182f06f5ec4225bf80bb99facf3366b5e12c740aff68b3cc5210086&"
      },
      "footer": {
        "text": "Posted by Cute Cats\n"
      },
      "timestamp": "2025-06-24T01:00:00:000Z"
    }
  ],
  "allowed_mentions": {
    "parse": [],
    "roles": [
      "747808586318610513"
    ]
  }
}

def send_discord_webhook(payload):
    headers = {
        "Content-Type": "application/json"
    }
    # This will raise requests.exceptions.RequestException if there's an HTTP error
    response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    print(f"Message sent successfully! Status code: {response.status_code}")

    
def fetch_rss_feed(url):
    """
    Fetches the RSS feed from the given URL.

    Args:
        url (str): The URL of the RSS feed.

    Returns:
        str: The content of the RSS feed as a string, or None if an error occurs.
    """
    try:
        response = requests.get(url, timeout=10) # Add a timeout for robustness
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return None

def extract_highest_chapter_number(rss_content):
    """
    Parses the RSS feed content and extracts the highest chapter number,
    only considering items with "line webtoon" in their description.

    Args:
        rss_content (str): The XML content of the RSS feed.

    Returns:
        int: The highest chapter number found, or 0 if no chapters are found or an error occurs.
    """
    highest_chapter = 0
    try:
        root = ET.fromstring(rss_content)
        # Find all 'item' elements within the RSS feed
        for item in root.findall('.//item'):
            title_element = item.find('title')
            description_element = item.find('description') # Get the description element

            if title_element is not None and description_element is not None:
                title = title_element.text
                description = description_element.text

                # Check if "line webtoon" is in the description (case-insensitive)
                if description and "line webtoon" in description.lower():
                    # Extract numbers from the title (e.g., "Omniscient Reader c.260")
                    # We'll look for numbers preceded by 'c.' or similar patterns.
                    # A more robust regex might be needed for different title formats.
                    try:
                        # Simple approach: find 'c.' and parse the number after it
                        chapter_str = title.split('c.')[-1].strip()
                        # Take only the numerical part if there's more text (e.g., "260 (END)")
                        chapter = int(''.join(filter(str.isdigit, chapter_str)))
                        if chapter > highest_chapter:
                            highest_chapter = chapter
                    except (ValueError, IndexError):
                        # Continue if chapter number cannot be parsed from a title
                        continue
    except ET.ParseError as e:
        print(f"Error parsing XML content: {e}")
    return highest_chapter

def read_chapter_from_file(file_path):
    """
    Reads the chapter number from the specified file.

    Args:
        file_path (str): The path to the file (e.g., 'feed.txt').

    Returns:
        int: The chapter number read from the file, or 0 if the file doesn't exist or is empty/invalid.
    """
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found. Assuming initial chapter is 0.")
        return 0
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            if content:
                return int(content)
            else:
                print(f"File '{file_path}' is empty. Assuming initial chapter is 0.")
                return 0
    except ValueError:
        print(f"Invalid content in '{file_path}'. Assuming initial chapter is 0.")
        return 0
    except IOError as e:
        print(f"Error reading from file '{file_path}': {e}")
        return 0

def write_chapter_to_file(file_path, chapter_number):
    """
    Writes the given chapter number to the specified file.

    Args:
        file_path (str): The path to the file.
        chapter_number (int): The chapter number to write.
    """
    # This will raise IOError if there's a problem writing to the file
    with open(file_path, 'w') as f:
        f.write(str(chapter_number))
    print(f"Updated '{file_path}' with chapter: {chapter_number}")

def main():
    """
    Main function to fetch, compare, and update the chapter number.
    """
    rss_feed_url = "https://api.mangaupdates.com/v1/series/50369844984/rss"
    file_path = "./orvcord/feed.txt"

    print(f"Fetching RSS feed from: {rss_feed_url}")
    rss_content = fetch_rss_feed(rss_feed_url)

    if rss_content:
        fetched_highest_chapter = extract_highest_chapter_number(rss_content)
        if fetched_highest_chapter == 0:
            print("No valid chapter numbers found in the feed or parsing error occurred.")
            return

        print(f"Highest chapter number fetched from feed: {fetched_highest_chapter}")

        current_saved_chapter = read_chapter_from_file(file_path)
        print(f"Current highest chapter number saved in '{file_path}': {current_saved_chapter}")

        if fetched_highest_chapter > current_saved_chapter:
            print(f"The fetched chapter ({fetched_highest_chapter}) is BIGGER than the saved chapter ({current_saved_chapter}).")
            send_discord_webhook(DISCORD_MESSAGE_PAYLOAD) # This will now throw an error on failure
            write_chapter_to_file(file_path, fetched_highest_chapter) # This will now throw an error on failure
        elif fetched_highest_chapter < current_saved_chapter:
            print(f"The fetched chapter ({fetched_highest_chapter}) is SMALLER than the saved chapter ({current_saved_chapter}).")
        else:
            print(f"The fetched chapter ({fetched_highest_chapter}) is the SAME as the saved chapter ({current_saved_chapter}).")
    else:
        print("Failed to retrieve RSS feed content. Cannot proceed with comparison.")

if __name__ == "__main__":
    main()
