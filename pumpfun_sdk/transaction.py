import base64
import json
import struct
from hashlib import sha256
from solders.transaction import VersionedTransaction
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta as SoldersAccountMeta
from solders.transaction import Transaction
from solders.keypair import Keypair
from spl.token.instructions import get_associated_token_address
from pumpfun_sdk.config import (
    PUMP_PROGRAM, 
    PUMP_GLOBAL, 
    PUMP_FEE, 
    LAMPORTS_PER_SOL, 
    TOKEN_DECIMALS, 
    BUY_DISCRIMINATOR, 
    SELL_DISCRIMINATOR
)
from solders.message import Message
from solders.hash import Hash
from pumpfun_sdk.idl import load_pump_idl

# Instead of inheriting, create a function to convert to SoldersAccountMeta
class AccountMeta:
    def __init__(self, pubkey: Pubkey, is_signer: bool, is_writable: bool):
        if not isinstance(pubkey, Pubkey):
            raise ValueError("Invalid pubkey: must be a Pubkey instance")
        self.pubkey = pubkey
        self.is_signer = is_signer
        self.is_writable = is_writable

    def to_solders(self) -> SoldersAccountMeta:
        return SoldersAccountMeta(self.pubkey, self.is_signer, self.is_writable)

def load_transaction(file_path: str) -> dict:
    """Load raw transaction JSON data from a file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def get_instruction_discriminator(instruction_name: str) -> bytes:
    """
    Compute the 8-byte discriminator for an instruction name using Anchor's convention.
    The discriminator is calculated as the first 8 bytes of SHA256("global:" + instruction_name).
    """
    return sha256(("global:" + instruction_name).encode("utf-8")).digest()[:8]

def get_instruction_name(idl: dict, ix_data: bytes) -> str:
    """
    Given an IDL and instruction data, extract the 8-byte discriminator from ix_data and 
    return the matching instruction's name from the IDL. If no match is found, return "unknown".
    """
    discriminator = ix_data[:8]
    for instruction in idl.get("instructions", []):
        inst_name = instruction.get("name")
        if get_instruction_discriminator(inst_name) == discriminator:
            return inst_name
    return "unknown"

def decode_transaction(tx_data: dict, idl: dict = None) -> list:
    """
    Decode a versioned transaction and extract its instructions.
    
    :param tx_data: A dictionary containing base64-encoded transaction data. 
                   It must include a "transaction" key with the encoded transaction(s).
    :param idl: Optional dictionary representing the Interface Definition Language 
               used to decode instructions. If not provided, uses the built-in Pump Fun IDL.
    :return: A list of decoded instructions. Each instruction is represented as a
             dictionary containing keys such as 'programId', 'instruction_name', 'data', and 'accounts'.
    :raises ValueError: If the transaction data is invalid.
    """
    if not isinstance(tx_data, dict) or 'transaction' not in tx_data:
        raise ValueError("Invalid transaction data")

    # Use built-in IDL if none provided
    if idl is None:
        idl = load_pump_idl()

    # Decode the base64-encoded transaction
    tx_data_decoded = base64.b64decode(tx_data['transaction'][0])
    transaction = VersionedTransaction.from_bytes(tx_data_decoded)
    instructions = transaction.message.instructions

    decoded_instructions = []
    account_keys = transaction.message.account_keys

    for ix in instructions:
        ix_data_bytes = bytes(ix.data)
        # Use the provided IDL to look up the instruction name based on its discriminator.
        inst_name = get_instruction_name(idl, ix_data_bytes) if idl is not None else "unknown"
        program_id = str(account_keys[ix.program_id_index])
        
        decoded_instructions.append({
            "programId": program_id,
            "instruction_name": inst_name,
            "data": ix_data_bytes.hex(),
            "accounts": [str(account_keys[i]) for i in ix.accounts]
        })
    return decoded_instructions

# More decoder functions can be added here for specialized instructions.

async def build_buy_transaction(
    payer: Keypair,
    mint: Pubkey,
    bonding_curve: Pubkey,
    associated_bonding_curve: Pubkey,
    amount: float,
    slippage: float = 0.25
) -> Transaction:
    """Build a buy transaction for a Pump token."""
    # Validate amount
    if amount <= 0:
        raise ValueError("Amount must be greater than 0")

    associated_token_account = get_associated_token_address(payer.pubkey(), mint)
    
    accounts = [
        AccountMeta(pubkey=PUMP_GLOBAL, is_signer=False, is_writable=False),
        AccountMeta(pubkey=PUMP_FEE, is_signer=False, is_writable=True),
        AccountMeta(pubkey=payer.pubkey(), is_signer=True, is_writable=True),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=True),
        AccountMeta(pubkey=bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=associated_bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=associated_token_account, is_signer=False, is_writable=True)
    ]
    
    # Convert amount to lamports
    amount_lamports = int(amount * LAMPORTS_PER_SOL)
    
    # Build instruction data
    data = bytearray(BUY_DISCRIMINATOR)
    data.extend(amount_lamports.to_bytes(8, 'little'))
    
    instruction = Instruction(
        program_id=PUMP_PROGRAM,
        accounts=[account.to_solders() for account in accounts],
        data=bytes(data)
    )
    
    # Create Message from instruction with proper Hash
    message = Message.new_with_blockhash(
        [instruction],
        payer.pubkey(),
        Hash.default()  # Use Hash.default() instead of Pubkey.default()
    )

    # Create transaction with message
    transaction = Transaction(
        from_keypairs=[payer],
        message=message,
        recent_blockhash=Hash.default()  # Use Hash here too
    )
    return transaction

async def build_sell_transaction(
    payer: Keypair,
    mint: Pubkey,
    bonding_curve: Pubkey,
    associated_bonding_curve: Pubkey,
    amount: float,
    slippage: float = 0.25
) -> Transaction:
    """Build a sell transaction for a Pump token."""
    # Validate amount
    if amount <= 0:
        raise ValueError("Amount must be greater than 0")

    associated_token_account = get_associated_token_address(payer.pubkey(), mint)
    
    accounts = [
        AccountMeta(pubkey=PUMP_GLOBAL, is_signer=False, is_writable=False),
        AccountMeta(pubkey=PUMP_FEE, is_signer=False, is_writable=True),
        AccountMeta(pubkey=payer.pubkey(), is_signer=True, is_writable=True),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=True),
        AccountMeta(pubkey=bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=associated_bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=associated_token_account, is_signer=False, is_writable=True)
    ]
    
    # Convert amount to token units
    token_amount = int(amount * (10 ** TOKEN_DECIMALS))
    
    # Build instruction data
    data = bytearray(SELL_DISCRIMINATOR)  # Use discriminator directly
    data.extend(token_amount.to_bytes(8, 'little'))
    
    instruction = Instruction(
        program_id=PUMP_PROGRAM,
        accounts=[account.to_solders() for account in accounts],
        data=bytes(data)
    )
    
    # Create Message from instruction with proper Hash
    message = Message.new_with_blockhash(
        [instruction],
        payer.pubkey(),
        Hash.default()  # Use Hash.default() instead of Pubkey.default()
    )

    # Create transaction with message
    transaction = Transaction(
        from_keypairs=[payer],
        message=message,
        recent_blockhash=Hash.default()  # Use Hash here too
    )
    return transaction 