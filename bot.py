import asyncio
import nest_asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram import InputFile, Update
from telegram.ext import ContextTypes
import os
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.types import TxOpts
from dotenv import load_dotenv
from base64 import b64decode

# Load environment variables
load_dotenv()

# Apply nest_asyncio to allow running the event loop in environments where it's already running
nest_asyncio.apply()

# Set up the bot token and load it from an environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
WALLET_PRIVATE_KEY = b64decode(os.getenv("WALLET_PRIVATE_KEY"))  # Base64 encoded private key
WALLET_PUBLIC_KEY = PublicKey(os.getenv("WALLET_PUBLIC_KEY"))
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL")
TOKEN_MINT_ADDRESS = PublicKey(os.getenv("TOKEN_MINT_ADDRESS"))

# Initialize Solana client and Keypair
solana_client = AsyncClient(SOLANA_RPC_URL)
wallet_keypair = Keypair.from_secret_key(WALLET_PRIVATE_KEY)

# Dictionary to track user progress and store user wallet addresses
user_data = {}

# Define states for conversation handler
ASK_WALLET_ADDRESS = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the conversation and ask the user for their Solana wallet address."""
    await update.message.reply_text("Welcome to the Tap to Make J. Bunny Kiss Boosey game! Please enter your Solana wallet address to start:")
    return ASK_WALLET_ADDRESS

async def ask_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store the user's Solana wallet address and welcome them to the game."""
    user_id = update.effective_user.id
    wallet_address = update.message.text.strip()

    try:
        # Validate the wallet address
        user_wallet_address = PublicKey(wallet_address)
        user_data[user_id] = {
            'wallet_address': user_wallet_address,
            'taps': 0
        }
        await update.message.reply_text("Thank you! Now, start tapping. Tap 10 times to make J. Bunny kiss Boosey!")
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text("That doesn't seem like a valid Solana wallet address. Please try again.")
        return ASK_WALLET_ADDRESS

async def tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the tap command."""
    user_id = update.effective_user.id

    # Check if the user has provided a wallet address
    if user_id not in user_data:
        await update.message.reply_text("Please enter your Solana wallet address first by using the /start command.")
        return

    # Increment tap count
    user_data[user_id]['taps'] += 1
    taps_remaining = 10 - user_data[user_id]['taps']

    if taps_remaining > 0:
        await update.message.reply_text(f"You've tapped! {taps_remaining} more taps to make J. Bunny kiss Boosey!")
    else:
        await update.message.reply_photo(photo=InputFile('Jbunny_kissing_boosey.png'),
                                         caption="J. Bunny kissed Boosey! You've earned 10 J. Bunny tokens!")
        # Reset user progress
        user_data[user_id]['taps'] = 0
        # Transfer tokens to the user's wallet
        txn_hash = await transfer_tokens(user_data[user_id]['wallet_address'])
        await update.message.reply_text(f"Transaction successful! Here is your transaction signature: {txn_hash}")

async def transfer_tokens(user_wallet_address: PublicKey):
    """Transfer 10 J. Bunny tokens to the user's wallet."""
    transfer_amount = 10 * 10**9  # Assuming token has 9 decimal places

    txn = Transaction().add(
        transfer(
            TransferParams(
                from_pubkey=WALLET_PUBLIC_KEY,
                to_pubkey=user_wallet_address,
                lamports=transfer_amount,
            )
        )
    )response = await solana_client.send_transaction(
        txn,
        wallet_keypair,
        opts=TxOpts(skip_preflight=True),
    )

    return response['result']

def main():
    # Initialize the application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_WALLET_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_wallet_address)],
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tap))

    # Run the bot with polling
    application.run_polling()

if name == "__main__":
    asyncio.run(main())