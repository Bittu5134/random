
import requests
import xml.etree.ElementTree as ET
import os
import json
import re
from datetime import datetime # Import datetime for accurate timestamp

class ORVChapterMonitor:
    """
    Monitors the Omniscient Reader's Viewpoint RSS feed for new chapters
    and sends Discord notifications.
    """

    def __init__(self, webhook_url, rss_feed_url, chapter_file_path):
        """
        Initializes the monitor with necessary URLs and file paths.

        Args:
            webhook_url (str): Discord webhook URL.
            rss_feed_url (str): URL of the RSS feed to monitor.
            chapter_file_path (str): Path to the file storing the last known chapter number.
        """
        self.webhook_url = webhook_url
        self.rss_feed_url = rss_feed_url
        self.chapter_file_path = chapter_file_path
        self._validate_webhook_url()

    def _validate_webhook_url(self):
        """Ensures the webhook URL is set, otherwise raises an error."""
        if not self.webhook_url:
            raise ValueError("WEBHOOK_URL environment variable not set. Please set it before running the script.")

    def _generate_discord_payload(self, chapter_number):
        """
        Generates the Discord message payload for a new chapter notification.

        Args:
            chapter_number (int): The newly released chapter number.

        Returns:
            dict: The Discord webhook payload.
        """
        # Ensure the timestamp is dynamic for each new notification
        current_timestamp = datetime.utcnow().isoformat() + "Z"
        
        return {
            "username": "ORV News",
            "embeds": [
                {
                    "author": {
                        "name": "✨ ORV: The Story Continues.."
                    },
                    "title": f"> Chapter {chapter_number} is here!\n> The tension rises and new twists await—dive into the chaos of the next scenario with Kim Dokja and the companions.\n> Catch up now on Webtoon before spoilers find you!",
                    "color": 4810725,
                    "fields": [
                        {
                            "name": "📖 Chapter",
                            "value": f"Episode {chapter_number} – Omniscient Reader's Viewpoint"
                        },
                        {
                            "name": "📅 Released On",
                            "value": datetime.now().strftime("%B %d, %Y") # Dynamic release date
                        },
                        {
                            "name": "🔗 Read Now",
                            "value": f"[Click here to read on Webtoon](https://m.webtoons.com/en/action/omniscient-reader/episode-{chapter_number}/viewer?title_no=2154&episode_no={chapter_number + 1})" # Adjusted episode_no
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
                        "text": "Posted by Cute Cats"
                    },
                    "timestamp": current_timestamp
                }
            ],
            "allowed_mentions": {
                "parse": [],
                "roles": [
                    "747808586318610513"
                ]
            }
        }

    def send_discord_webhook(self, chapter_number):
        """
        Sends a Discord webhook notification with the given payload.

        Args:
            chapter_number (int): The chapter number to include in the notification.

        Raises:
            requests.exceptions.RequestException: If there's an HTTP error during the request.
        """
        payload = self._generate_discord_payload(chapter_number)
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(self.webhook_url, data=json.dumps(payload), headers=headers, timeout=10)
            response.raise_for_status()
            print(f"Discord message for chapter {chapter_number} sent successfully! Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending Discord webhook for chapter {chapter_number}: {e}")
            raise # Re-raise the exception for upstream handling

    def fetch_rss_feed(self):
        """
        Fetches the RSS feed content from the configured URL.

        Returns:
            bytes: The content of the RSS feed, or None if an error occurs.
        """
        print(f"Fetching RSS feed from: {self.rss_feed_url}")
        try:
            response = requests.get(self.rss_feed_url, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching RSS feed: {e}")
            return None

    def extract_highest_chapter_number(self, rss_content):
        """
        Parses the RSS feed content and extracts the highest chapter number,
        considering only items with "line webtoon" in their description.

        Args:
            rss_content (bytes): The XML content of the RSS feed.

        Returns:
            int: The highest chapter number found, or 0 if no chapters are found or an error occurs.
        """
        highest_chapter = 0
        try:
            root = ET.fromstring(rss_content)
            for item in root.findall('.//item'):
                title_element = item.find('title')
                description_element = item.find('description')

                if title_element is not None and description_element is not None:
                    title = title_element.text
                    description = description_element.text

                    if description and "line webtoon" in description.lower():
                        # More robust regex to find chapter numbers like 'c.260' or 'Chapter 260'
                        match = re.search(r'(?:c\.|Chapter)\s*(\d+)', title, re.IGNORECASE)
                        if match:
                            try:
                                chapter = int(match.group(1))
                                if chapter > highest_chapter:
                                    highest_chapter = chapter
                            except ValueError:
                                continue # Skip if chapter number cannot be parsed
        except ET.ParseError as e:
            print(f"Error parsing XML content: {e}")
        return highest_chapter

    def read_chapter_from_file(self):
        """
        Reads the chapter number from the configured file.

        Returns:
            int: The chapter number read from the file, or 0 if file issues occur.
        """
        if not os.path.exists(self.chapter_file_path):
            print(f"File '{self.chapter_file_path}' not found. Assuming initial chapter is 0.")
            return 0
        try:
            with open(self.chapter_file_path, 'r') as f:
                content = f.read().strip()
                return int(content) if content else 0
        except (ValueError, IOError) as e:
            print(f"Error reading from or invalid content in '{self.chapter_file_path}': {e}. Assuming initial chapter is 0.")
            return 0

    def write_chapter_to_file(self, chapter_number):
        """
        Writes the given chapter number to the configured file.

        Args:
            chapter_number (int): The chapter number to write.
        """
        try:
            os.makedirs(os.path.dirname(self.chapter_file_path), exist_ok=True) # Create directory if it doesn't exist
            with open(self.chapter_file_path, 'w') as f:
                f.write(str(chapter_number))
            print(f"Updated '{self.chapter_file_path}' with chapter: {chapter_number}")
        except IOError as e:
            print(f"Error writing to file '{self.chapter_file_path}': {e}")
            raise # Re-raise the exception for upstream handling

    def run(self):
        """
        Executes the monitoring logic: fetches RSS, compares chapter numbers,
        sends notifications, and updates the chapter file.
        """
        rss_content = self.fetch_rss_feed()

        if not rss_content:
            print("Failed to retrieve RSS feed content. Cannot proceed with comparison.")
            return

        fetched_highest_chapter = self.extract_highest_chapter_number(rss_content)
        if fetched_highest_chapter == 0:
            print("No valid chapter numbers found in the feed or parsing error occurred.")
            return

        print(f"Highest chapter number fetched from feed: {fetched_highest_chapter}")

        current_saved_chapter = 0
        # current_saved_chapter = self.read_chapter_from_file()
        print(f"Current highest chapter number saved in '{self.chapter_file_path}': {current_saved_chapter}")

        if fetched_highest_chapter > current_saved_chapter:
            print(f"The fetched chapter ({fetched_highest_chapter}) is BIGGER than the saved chapter ({current_saved_chapter}). Notifying Discord...")
            try:
                self.send_discord_webhook(fetched_highest_chapter)
                self.write_chapter_to_file(fetched_highest_chapter)
            except (requests.exceptions.RequestException, IOError):
                print("An error occurred during notification or file write. The chapter file might not be updated.")
        elif fetched_highest_chapter < current_saved_chapter:
            print(f"The fetched chapter ({fetched_highest_chapter}) is SMALLER than the saved chapter ({current_saved_chapter}). This might indicate an issue with the RSS feed or file. No action taken.")
        else:
            print(f"The fetched chapter ({fetched_highest_chapter}) is the SAME as the saved chapter ({current_saved_chapter}). No new chapter.")

if __name__ == "__main__":
    WEBHOOK_URL = "https://discord.com/api/webhooks/1387003307066916946/f-HmMpXXhPUMd5rura0mXtQ6SQ4y4JTQD4mGSfPdDUOSsqoA1rfdZnV_4El2-iJqqYcn"
    # WEBHOOK_URL = os.environ.get('WEBHOOK')
    RSS_FEED_URL = "https://api.mangaupdates.com/v1/series/50369844984/rss"
    CHAPTER_FILE_PATH = "./orvcord/feed.txt"

    try:
        monitor = ORVChapterMonitor(WEBHOOK_URL, RSS_FEED_URL, CHAPTER_FILE_PATH)
        monitor.run()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)
