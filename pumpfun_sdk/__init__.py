"""
PumpFun SDK
===========

A Python toolkit for interacting with PumpFun programs on the Solana blockchain.
This SDK provides interfaces for creating, decoding, and analyzing transactions,
managing bonding curves, and subscribing to on-chain events.

Basic usage:
-----------
    from pumpfun_sdk import SolanaClient, BondingCurveState
    from pumpfun_sdk.utils import process_bonding_curve_state

    # Initialize client
    client = SolanaClient()
    
    # Get bonding curve state
    curve_state = await process_bonding_curve_state("YourBondingCurveAddress")

Available modules:
----------------
- client: Solana RPC client wrapper
- pump_curve: Bonding curve state parsing and price calculation
- transaction: Transaction loading and decoding with IDL support
- utils: Helper functions for common operations
"""

# Version of the pumpfun-sdk package
__version__ = "0.1.0"

# Import main classes and functions for easy access
from .client import SolanaClient

# Import configuration
from .config import (
    LAMPORTS_PER_SOL,
    PUMP_LIQUIDITY_MIGRATOR,
    PUMP_PROGRAM,
    RPC_ENDPOINT,
    TOKEN_DECIMALS,
    WSS_ENDPOINT,
)
from .idl import load_pump_idl, load_raydium_idl
from .pump_curve import BondingCurveState, calculate_bonding_curve_price
from .transaction import (
    AccountMeta,
    build_buy_transaction,
    build_sell_transaction,
    decode_transaction,
    get_instruction_name,
    load_transaction,
)
from .utils import process_bonding_curve_state, subscribe_to_events

# Define what should be available when using "from pumpfun_sdk import *"
__all__ = [
    # Main classes
    "SolanaClient",
    "BondingCurveState",
    # Core functions
    "calculate_bonding_curve_price",
    "load_transaction",
    "decode_transaction",
    "get_instruction_name",
    "AccountMeta",
    "build_buy_transaction",
    "build_sell_transaction",
    "subscribe_to_events",
    "process_bonding_curve_state",
    # Configuration
    "RPC_ENDPOINT",
    "WSS_ENDPOINT",
    "PUMP_PROGRAM",
    "PUMP_LIQUIDITY_MIGRATOR",
    "LAMPORTS_PER_SOL",
    "TOKEN_DECIMALS",
    # IDL functions
    "load_pump_idl",
    "load_raydium_idl",
]
