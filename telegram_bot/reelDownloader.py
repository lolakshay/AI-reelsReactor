import requests
import re
from urllib.parse import quote

# The address of your local scraping API
# Make sure your Node.js server is running before executing this script.
LOCAL_API_BASE_URL = "http://localhost:3000/igdl"


def get_video_details(reel_url):
    """
    Calls the local API to get the direct video URL and metadata.
    """
    print("-> Step 1: Fetching video metadata from local API...")

    # Construct the full API URL, ensuring the reel_url is URL-encoded
    api_url = f"{LOCAL_API_BASE_URL}?url={quote(reel_url)}"

    try:
        response = requests.get(api_url)
        # Raise an error for bad status codes (4xx or 5xx)
        response.raise_for_status()

        data = response.json()

        # Navigate the JSON structure to find the direct video URL
        video_url = data['url']['data'][0]['url']
        print("   ✓ Metadata received.")
        return video_url

    except requests.exceptions.RequestException as e:
        print(f"   ✗ Error: Could not connect to the local API at {LOCAL_API_BASE_URL}.")
        print(f"   Please ensure your backend server is running. Details: {e}")
        return None
    except (KeyError, IndexError):
        print("   ✗ Error: The API response did not contain a valid video URL.")
        return None


def generate_filename(reel_url):
    """
    Generates a filename like 'instagram_reel_{id}.mp4' from the URL.
    """
    # Regex to find the unique ID in the reel URL
    match = re.search(r'reel/([a-zA-Z0-9_-]+)', reel_url)
    if match and match.group(1):
        video_id = match.group(1)
        return f"instagram_reel_{video_id}.mp4"
    else:
        # Fallback filename if the ID can't be found
        return "downloaded_reel.mp4"


def download_video_file(video_url, filename):
    """
    Downloads the video from the direct URL and saves it to a file.
    """
    print(f"-> Step 2: Downloading video to '{filename}'...")
    try:
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            # Open a file in binary write mode
            with open(filename, 'wb') as f:
                # Write the video content in chunks to handle large files
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"   ✓ Download complete! Video saved as '{filename}'.")

    except requests.exceptions.RequestException as e:
        print(f"   ✗ Error: Failed to download the video file. Details: {e}")


def main():
    """
    Main function to run the downloader.
    """
    # Get the URL from the user
    reel_url = input("Please paste the Instagram Reel URL and press Enter: ")

    # Basic validation of the URL
    if "instagram.com/reel/" not in reel_url:
        print("✗ Invalid URL. Please provide a valid Instagram Reel link.")
        return

    # 1. Get the direct video URL from the local API
    direct_video_url = get_video_details(reel_url)

    if direct_video_url:
        # 2. Generate a unique filename
        output_filename = generate_filename(reel_url)

        # 3. Download and save the video file
        download_video_file(direct_video_url, output_filename)


if __name__ == "__main__":
    main()