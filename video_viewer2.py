import google.generativeai as genai
import os

# 1. Configure your API key
# Replace "YOUR_API_KEY" with the key you got from Google AI Studio.
genai.configure(api_key="*")

# 2. Define the LLM to use
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# The video URL from your downloader
video_url_from_downloader = "https://d.rapidcdn.app/v2?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJodHRwczovL3Njb250ZW50LWNkZzQtMS5jZG5pbnN0YWdyYW0uY29tL28xL3YvdDE2L2YyL204Ni9BUU5tdldnUVJLTkdrN203cWtYYmUzTnFVaTNoenY2aUZSZ1FLNnVWWXhkcEpZakhuYjhNcXRZX3J6d2t2aF8zVzRCVUJMM28wbjdLSVowLURmM0pPa1dManZiOEV1ZjBwUW1QcXg4Lm1wND9zdHA9ZHN0LW1wNCZlZmc9ZXlKeFpWOW5jbTkxY0hNaU9pSmJYQ0pwWjE5M1pXSmZaR1ZzYVhabGNubGZkblJ6WDI5MFpsd2lYU0lzSW5abGJtTnZaR1ZmZEdGbklqb2lkblJ6WDNadlpGOTFjbXhuWlc0dVkyeHBjSE11WXpJdU56SXdMbUpoYzJWc2FXNWxJbjAmX25jX2NhdD0xMDImdnM9MTI4NjkzNDQ3OTQ5MjU5M180MjI5OTExMzkmX25jX3ZzPUhCa3NGUUlZVW1sblgzaHdkbDl5WldWc2MxOXdaWEp0WVc1bGJuUmZjM0pmY0hKdlpDOUNNalEwUlRkR056ZEZRa1UyUlRSQ01rRkdSamswTnpreVF6Y3pORGc1UTE5MmFXUmbiMTlrWVhOb2FXNXBkQzV0Y0RRVkFBTElBUklBRlFJWU9uQmhjM04wYUhKdmRXZG9YMlYyWlhKemRHOXlaUzlIUnpKa1NuZzRaRzlsV21veE1VbEtRVWRGVDNWbll6RnpWSGhIWW5GZlJVRkJRVVlWQWdMSUFSSUFLQUFZQUJzQUZRQUFKcFRCN0s3TnFiOCUyRkZRSW9Ba016TEJkQUg5MHZHcCUyQiUyQmR4Z1NaR0Z6YUY5aVlYTmbiGwx1WlY4eFgzWXhFUUIxJTJGZ2RsNXAwQkFBJTNEJTNEJmNjYj05LTQmb2g9MDBfQWZhbDJRYWl2VGFyS0RJUFpZOW05M2ppQTlkUEd0Y0EzY3dWS2JIU1YtdmJKQSZvZT02OEM4QjA5QSZfbmNfc2lkPTEwZDEzYiIsImZpbGVuYW1lIjoic25hcHNhdmUtYXBwXzM2ODUzMDM3ODUwNjM4NzMwMzQubXA0IiwiaGVhZGVycyI6eyJ1c2VyLWFnZW50IjoiVGVsZWdyYW1Cb3QgKGxpa2UgVHdpdHRlckJvdCkifSwiaWF0IjoxNzU3ODU3ODM4fQ.P2W34X7znh6Tj8cxxVx4NhgzRVFXYZ2v5zEROlY69Nw&dl=1&dl=1"

# 3. Create the parts for the API request
# Corrected syntax: 'file_data' with an underscore.
contents = [
    {
        "role": "user",
        "parts": [
            {
                "text": "Watch this video and provide a detailed summary. Also, identify the main subject and describe the setting. Reply as if you are a professional film critic."
            },
            {
                "file_data": {  # Changed from 'fileData' to 'file_data'
                    "mime_type": "video/mp4", # Changed from 'mimeType' to 'mime_type'
                    "file_uri": video_url_from_downloader # Changed from 'fileUri' to 'file_uri'
                }
            }
        ]
    }
]

# 4. Make the API call
try:
    print("Sending video and prompt to Gemini...")
    response = model.generate_content(
        contents=contents
    )

    # 5. Print the LLM's response
    print("\n--- AI Analysis ---")
    print(response.text)
    print("\n-------------------")

except Exception as e:
    print(f"An error occurred during API call: {e}")
