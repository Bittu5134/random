import requests
import xml.etree.ElementTree as ET
import os

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
    Parses the RSS feed content and extracts the highest chapter number.

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
            if title_element is not None:
                title = title_element.text
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
    try:
        with open(file_path, 'w') as f:
            f.write(str(chapter_number))
        print(f"Updated '{file_path}' with chapter: {chapter_number}")
    except IOError as e:
        print(f"Error writing to file '{file_path}': {e}")

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
            write_chapter_to_file(file_path, fetched_highest_chapter)
        elif fetched_highest_chapter < current_saved_chapter:
            print(f"The fetched chapter ({fetched_highest_chapter}) is SMALLER than the saved chapter ({current_saved_chapter}).")
        else:
            print(f"The fetched chapter ({fetched_highest_chapter}) is the SAME as the saved chapter ({current_saved_chapter}).")
    else:
        print("Failed to retrieve RSS feed content. Cannot proceed with comparison.")

if __name__ == "__main__":
    main()
