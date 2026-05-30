import telebot
import requests
import re
from urllib.parse import quote
import google.generativeai as genai
import time
import os

# The specific 'ClientError' import is removed.

# --- CONFIGURATION ---
BOT_TOKEN = "*"
GEMINI_API_KEY = "*"
LOCAL_API_BASE_URL = "http://localhost:3000/igdl"
PROMPT_TEXT = "Imagine you’re my close friend. I just sent you a reel — 99% of the time, react exactly like a friend would using only a single emoji, but occasionally you can add a short text reply instead."

# --- INITIALIZE BOTS/CLIENTS ---
bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)


# --- DOWNLOADER HELPER FUNCTIONS ---
def get_direct_video_url(reel_url):
    print(f"-> Processing URL: {reel_url}")
    api_url = f"{LOCAL_API_BASE_URL}?url={quote(reel_url)}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        video_url = data['url']['data'][0]['url']
        print("   ✓ Found direct video link.")
        return video_url
    except Exception as e:
        print(f"   ✗ Error getting direct URL: {e}")
        return None


def generate_filename(reel_url):
    match = re.search(r'reel/([a-zA-Z0-9_-]+)', reel_url)
    if match and match.group(1):
        video_id = match.group(1)
        return f"instagram_reel_{video_id}.mp4"
    return "downloaded_reel.mp4"


def download_video_locally(video_url, filename):
    print(f"-> Downloading video to local file: '{filename}'...")
    try:
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"   ✓ Download complete!")
        return True
    except Exception as e:
        print(f"   ✗ Error downloading video file: {e}")
        return False


# --- GEMINI HELPER FUNCTION ---
def analyze_video_with_gemini(video_path):
    print(f"-> Starting Gemini processing for {video_path}...")
    video_file_resource = None
    try:
        print("   Uploading file to Gemini...")
        video_file_resource = genai.upload_file(path=video_path)
        print(f"   File uploaded successfully: {video_file_resource.name}")

        print("   Waiting for file processing...")
        while video_file_resource.state.name == "PROCESSING":
            time.sleep(5)
            video_file_resource = genai.get_file(name=video_file_resource.name)

        if video_file_resource.state.name != "ACTIVE":
            print(f"   ✗ File processing failed. Final state: {video_file_resource.state.name}")
            return None

        print("   ✓ File is ACTIVE. Generating content...")

        model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
        response = model.generate_content([PROMPT_TEXT, video_file_resource])

        print(f"   ✓ Gemini response received: {response.text}")
        return response.text.strip()

    # --- MODIFICATION IS HERE ---
    # We now catch any generic Exception instead of the specific ClientError.
    except Exception as e:
        print(f"   ✗ An error occurred during Gemini processing: {e}")
        return None
    # --- END OF MODIFICATION ---
    finally:
        if video_file_resource:
            genai.delete_file(name=video_file_resource.name)
            print(f"   ✓ Cleaned up Gemini file: {video_file_resource.name}")


# --- MAIN TELEGRAM BOT HANDLER ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    local_filename = None
    try:
        if "instagram.com/reel/" in message.text:
            #bot.reply_to(message, "✅ Link received. Starting the process...")

            direct_url = get_direct_video_url(message.text)
            if not direct_url:
                bot.reply_to(message, "❌ I am Busy Right now, Sorry :(")
                return

            local_filename = generate_filename(message.text)
            if not download_video_locally(direct_url, local_filename):
                bot.reply_to(message, "❌ I am Busy Right now, Sorry :(")
                return

            #bot.send_message(message.chat.id, "🧠 Video downloaded. Sending to Gemini for analysis...")
            reaction = analyze_video_with_gemini(local_filename)

            if reaction:
                bot.reply_to(message, reaction)
            else:
                bot.reply_to(message, "❌ I am Busy Right now, Sorry :(")
        #else:
           # bot.reply_to(message, "👋 Hello! Please send an Instagram Reel link.")

    except Exception as e:
        print(f"An error occurred in the main handler: {e}")
        bot.reply_to(message, "🤖 Oops! Something went wrong on my end.")
    finally:
        if local_filename and os.path.exists(local_filename):
            os.remove(local_filename)
            print(f"✓ Cleaned up local file: {local_filename}")


# --- START THE BOT ---
print("🚀 Full Pipeline Bot is running...")
bot.polling(none_stop=True)
