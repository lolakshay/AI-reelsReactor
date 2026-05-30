import telebot
from datetime import datetime

# --- CONFIGURATION ---
# Replace this with the token you got from @BotFather
BOT_TOKEN = "8117177812:AAEh8GBWIpYI3Vry7rYBlYKJ-aJk-DtbuBM"

# The name of the file where messages will be saved
LOG_FILE = "telegram_log.txt"

# --- INITIALIZE THE BOT ---
bot = telebot.TeleBot(BOT_TOKEN)


# --- DEFINE THE MESSAGE HANDLER ---
# This function will be called whenever the bot receives a text message.
@bot.message_handler(func=lambda message: True)
def save_message(message):
    """
    Saves the received message text to a local file.
    """
    try:
        # Get user information for context
        user_info = f"From: {message.from_user.first_name}"

        # Get the message text
        message_text = message.text



        # Format the log entry
        log_entry = f" {user_info}\nMessage: {message_text}\n--------------------\n"

        # Open the file in 'append' mode (a) and write the new log entry
        # Using 'with' ensures the file is properly closed even if errors occur.
        # 'encoding="utf-8"' is important to handle emojis and special characters.
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(f"Saved message from {message.from_user.first_name}")

        # Optional: Send a confirmation message back to the user
        bot.reply_to(message, "😂😂")

    except Exception as e:
        print(f"An error occurred: {e}")
        bot.reply_to(message, "❌ Sorry, there was an error saving your message.")


# --- START THE BOT ---
if __name__ == "__main__":
    print("Bot is running and listening for messages...")
    # bot.polling() makes the bot continuously check for new messages.
    bot.polling(none_stop=True)