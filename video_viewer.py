from google import genai
import time
from google.genai.errors import ClientError

# 1. WARNING: Replace this with your actual key for local testing.
API_KEY = "*"

# 2. Define the path to your video file
VIDEO_FILE_PATH = "sample_video.mp4"  # Assuming you fixed this path
PROMPT_TEXT = ("imagine you are a friend of mine, i sent you a reels to watch, react like they would, give only one emoji as a reaction")

# 3. Initialize the client
client = genai.Client(api_key=API_KEY)

# --- Main Logic ---
print(f"Uploading file: {VIDEO_FILE_PATH}...")
video_file = client.files.upload(file=VIDEO_FILE_PATH)
print(f"File uploaded successfully: {video_file.name}")

##  *** NEW LOGIC START: Wait for the file to be ACTIVE ***
MAX_WAIT_TIME_SECONDS = 300  # 5 minutes
check_interval_seconds = 10
start_time = time.time()

print("Waiting for file processing to complete...")

while video_file.state == "PROCESSING" and (time.time() - start_time) < MAX_WAIT_TIME_SECONDS:
    # Wait for the specified interval
    time.sleep(check_interval_seconds)

    # Re-fetch the file status from the API
    video_file = client.files.get(name=video_file.name)
    print(f"  Current state: {video_file.state} (Elapsed: {int(time.time() - start_time)}s)")

if video_file.state != "ACTIVE":
    # If we exit the loop and the state isn't ACTIVE, something went wrong
    print(f"\nERROR: File processing failed or timed out. Final state: {video_file.state}")
    # Still attempt to clean up
    client.files.delete(name=video_file.name)
    exit()

print(f"\nFile is ACTIVE. Processing can begin.")
## *** NEW LOGIC END ***

try:
    # Generate content by combining the text prompt and the uploaded file
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[PROMPT_TEXT, video_file]
    )

    print("\n--- Model Response ---")
    print(response.text)

except ClientError as e:
    print(f"\nAn API error occurred during content generation: {e}")

finally:
    # Clean up the uploaded file to avoid unnecessary storage
    client.files.delete(name=video_file.name)
    print(f"\nClean up complete. Deleted file: {video_file.name}")
