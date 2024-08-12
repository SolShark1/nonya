import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
REWARD_AMOUNT = int(os.getenv("REWARD_AMOUNT"))

# Create a dictionary to track user taps
user_taps = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_taps[user_id] = 0
    
    await update.message.reply_photo(
        photo=open('images/jbunny.png', 'rb'),
        caption="Tap the button 10 times to make JBunny kiss Boosey!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Tap to Kiss!", callback_data="tap")]
        ])
    )

async def tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in user_taps:
        user_taps[user_id] = 0

    user_taps[user_id] += 1

    if user_taps[user_id] < 10:
        await query.answer(f"{user_taps[user_id]} taps! Keep going!")
    else:
        await query.answer("JBunny is kissing Boosey! You've earned your reward!")
        await query.edit_message_media(
            media=open('images/jbunny_kissing_boosey.png', 'rb'),
            reply_markup=None
        )
        
        # Call the function to send tokens
        send_tokens(user_id)
        user_taps[user_id] = 0  # Reset taps for the user

def send_tokens(user_id):
    # Logic to send tokens using WALLET_PRIVATE_KEY and REWARD_AMOUNT
    # This is a placeholder; integrate with your blockchain logic
    print(f"Sending {REWARD_AMOUNT} tokens to user {user_id}!")

async def main():
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(tap, pattern="^tap$"))

    # Run the bot until Ctrl+C is pressed
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())