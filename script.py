from solana.transaction import Transaction
from solana.system_program import transfer
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.rpc.types import TxOpts
from solana.system_program import TransferParams
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve sensitive information from environment variables
secret_key_hex = os.getenv("SECRET_KEY")
receiver_pubkey_str = os.getenv("RECEIVER_PUBLIC_KEY")
transfer_amount = int(os.getenv("TRANSFER_AMOUNT"))

# Convert the secret key from hex format to bytes
secret_key_bytes = bytes.fromhex(secret_key_hex)
sender_keypair = Keypair.from_secret_key(secret_key_bytes)

# Create the public key for the receiver
receiver_pubkey = PublicKey(receiver_pubkey_str)

# Initialize the Solana client
client = Client("https://api.mainnet-beta.solana.com")

# Create the transaction
transaction = Transaction()

# Add the transfer instruction to the transaction
transfer_instruction = transfer(
    TransferParams(
        from_pubkey=sender_keypair.public_key,
        to_pubkey=receiver_pubkey,
        lamports=transfer_amount
    )
)
transaction.add(transfer_instruction)

# Send the transaction
try:
    # Sign and send the transaction
    response = client.send_transaction(transaction, sender_keypair, opts=TxOpts(skip_confirmation=False))
    print(f"Transaction sent: {response['result']}")
except Exception as e:
    print(f"An error occurred: {e}")