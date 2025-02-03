#!/usr/bin/env python
"""
Transaction Analysis Example for pumpfun_sdk.

This script demonstrates how to:
- Load a raw transaction from a file.
- Decode the transaction using a provided IDL.
- Print the decoded instructions.
"""

import asyncio

from pumpfun_sdk.idl import load_pump_idl
from pumpfun_sdk.transaction import (
    decode_transaction,
    get_instruction_discriminator,
    get_instruction_name,
    load_transaction,
)
from pumpfun_sdk.utils import decode_transaction_from_file


async def analyze_transaction():
    # Replace these with the actual paths to your files.
    tx_file = "path/to/transaction.json"
    idl_file = "path/to/idl.json"

    print("\n=== Analyzing Transaction ===")
    try:
        # This function will use the custom IDL file if provided,
        # otherwise it will fall back to the built-in Pump Fun IDL.
        await decode_transaction_from_file(tx_file, idl_file)
    except Exception as e:
        print(f"Error analyzing transaction: {e}")


async def main():
    try:
        await analyze_transaction()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
