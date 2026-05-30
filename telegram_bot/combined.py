import telebot
import requests
import re
from urllib.parse import quote

# --- CONFIGURATION ---

# Replace this with the token you got from @BotFather
BOT_TOKEN = "8117177812:AAEh8GBWIpYI3Vry7rYBlYKJ-aJk-DtbuBM"

# The address of your local scraping API.
# Make sure your Node.js server is running.
LOCAL_API_BASE_URL = "http://localhost:3000/igdl"

# --- INITIALIZE THE BOT ---
bot = telebot.TeleBot(BOT_TOKEN)


# --- DOWNLOADER HELPER FUNCTIONS ---

def get_direct_video_url(reel_url):
    """
    Calls the local API to get the direct video URL.
    Returns the URL as a string if successful, otherwise returns None.
    """
    print(f"-> Processing URL: {reel_url}")
    api_url = f"{LOCAL_API_BASE_URL}?url={quote(reel_url)}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        video_url = data['url']['data'][0]['url']
        print("   ✓ Found direct video link.")
        return video_url
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Error: Could not connect to the local API. Details: {e}")
        return None
    except (KeyError, IndexError):
        print("   ✗ Error: API response did not contain a valid video URL.")
        return None


def generate_filename(reel_url):
    """
    Generates a filename like 'instagram_reel_{id}.mp4' from the URL.
    """
    match = re.search(r'reel/([a-zA-Z0-9_-]+)', reel_url)
    if match and match.group(1):
        video_id = match.group(1)
        return f"instagram_reel_{video_id}.mp4"
    else:
        return "downloaded_reel.mp4"


def download_video_locally(video_url, filename):
    """
    Downloads the video from the direct URL and saves it to a local file.
    Returns True on success, False on failure.
    """
    print(f"-> Downloading video to local file: '{filename}'...")
    try:
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"   ✓ Download complete!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Error: Failed to download the video file. Details: {e}")
        return False


# --- TELEGRAM BOT MESSAGE HANDLER ---

# --- TELEGRAM BOT MESSAGE HANDLER (Corrected) ---

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """
    Handles incoming messages. If it's an Instagram Reel link,
    it downloads the video locally.
    """
    message_text = message.text

    if "instagram.com/reel/" in message_text:
        bot.reply_to(message, "⬇️ Link received. Starting local download...")

        # 1. Get the direct video URL
        direct_url = get_direct_video_url(message_text)

        if direct_url:
            # 2. Generate a unique filename for the local file
            local_filename = generate_filename(message_text)

            # 3. Download the video to the local machine
            success = download_video_locally(direct_url, local_filename)

            if success:
                # --- FIX IS HERE ---
                # 4a. Escape special characters in the filename for MarkdownV2
                escaped_filename = local_filename.replace('_', '\\_').replace('.', '\\.')

                # 4b. Create the reply text, escaping the '!'
                reply_text = f"✅ Download complete\! Saved locally as:\n`{escaped_filename}`"

                # 4c. Send the corrected message
                bot.reply_to(message, reply_text, parse_mode="MarkdownV2")
                # --- END OF FIX ---
            else:
                bot.reply_to(message, "❌ Sorry, an error occurred during the download process.")
        else:
            bot.reply_to(message, "❌ Could not get video link. Please check the URL and make sure the post is public.")
    else:
        bot.reply_to(message, "👋 Hello! Please send me an Instagram Reel link to download it to my local machine.")


# --- START THE BOT ---
if __name__ == "__main__":
    print("Local Downloader Bot is running...")
    bot.polling(none_stop=True)