import asyncio
import nest_asyncio
from telegram.ext import Application

# Apply nest_asyncio to allow running the event loop in environments where it's already running
nest_asyncio.apply()

async def main():
    # Initialize your application here (customize as needed)
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Run the bot with polling
    await application.run_polling()

# Entry point for the script
if name == "__main__":
    # This will start the event loop and run the main coroutine
    asyncio.run(main())