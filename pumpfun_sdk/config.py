"""
Configuration file for pumpfun-sdk.
Define endpoints and global addresses used across the SDK.
"""
import os
from solders.pubkey import Pubkey
from hashlib import sha256

# System & pump.fun addresses
PUMP_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PUMP_GLOBAL = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
PUMP_EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
PUMP_FEE = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
PUMP_LIQUIDITY_MIGRATOR = Pubkey.from_string("39azUYFWPz3VHgKCf3VChUwbpURdCHRxjWVowf5jUJjg")
SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
SYSTEM_TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
SYSTEM_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM_RENT = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
SOL = Pubkey.from_string("So11111111111111111111111111111111111111112")

# Blockchain parameters
LAMPORTS_PER_SOL = 1_000_000_000
TOKEN_DECIMALS = 6

# Trading parameters
BUY_AMOUNT = 0.0001  # Amount of SOL to spend when buying
BUY_SLIPPAGE = 0.2  # 20% slippage tolerance for buying
SELL_SLIPPAGE = 0.2  # 20% slippage tolerance for selling

# Instruction discriminators based on IDL instruction names
INITIALIZE_DISCRIMINATOR = sha256(b"global:initialize").digest()[:8]
SET_PARAMS_DISCRIMINATOR = sha256(b"global:setParams").digest()[:8]
CREATE_DISCRIMINATOR = sha256(b"global:create").digest()[:8]
BUY_DISCRIMINATOR = sha256(b"global:buy").digest()[:8]
SELL_DISCRIMINATOR = sha256(b"global:sell").digest()[:8]
WITHDRAW_DISCRIMINATOR = sha256(b"global:withdraw").digest()[:8]

# Default endpoints (can be overridden by environment variables)
DEFAULT_RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"
DEFAULT_WSS_ENDPOINT = "wss://api.mainnet-beta.solana.com"

# Get endpoints from environment variables or use defaults
RPC_ENDPOINT = os.getenv("SOLANA_RPC_ENDPOINT", DEFAULT_RPC_ENDPOINT)
WSS_ENDPOINT = os.getenv("SOLANA_WSS_ENDPOINT", DEFAULT_WSS_ENDPOINT)

# Private key (optional, for transaction signing)
PRIVATE_KEY = os.getenv("SOLANA_PRIVATE_KEY")

# Expected discriminator for bonding curve accounts
EXPECTED_DISCRIMINATOR = b"\xf8\x87\xe8\xba\x8f\x00\x00\x00"

def set_endpoints(rpc_endpoint: str = None, wss_endpoint: str = None):
    """
    Set custom RPC and WSS endpoints.
    
    :param rpc_endpoint: Custom RPC endpoint URL
    :param wss_endpoint: Custom WSS endpoint URL
    """
    global RPC_ENDPOINT, WSS_ENDPOINT
    
    if rpc_endpoint:
        RPC_ENDPOINT = rpc_endpoint
    if wss_endpoint:
        WSS_ENDPOINT = wss_endpoint

def get_endpoints():
    """
    Get current RPC and WSS endpoints.
    
    :return: Tuple of (RPC_ENDPOINT, WSS_ENDPOINT)
    """
    return RPC_ENDPOINT, WSS_ENDPOINT 