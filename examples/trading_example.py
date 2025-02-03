#!/usr/bin/env python
"""
Trading Example for pumpfun_sdk.

This script demonstrates how to build buy and sell transactions for a Pump token.
"""

import asyncio

from solders.keypair import Keypair
from solders.pubkey import Pubkey

from pumpfun_sdk import LAMPORTS_PER_SOL, PUMP_PROGRAM, SolanaClient
from pumpfun_sdk.transaction import build_buy_transaction, build_sell_transaction
from pumpfun_sdk.utils import process_bonding_curve_state


async def example_buy_tokens(
    buyer_keypair: Keypair,
    mint: Pubkey,
    bonding_curve: Pubkey,
    associated_bonding_curve: Pubkey,
    amount_sol: float,
):
    """
    Example of buying tokens using the pump.fun protocol
    """
    client = SolanaClient()
    try:
        # First check the current state and price
        print(f"\nChecking current state for mint: {mint}")
        await process_bonding_curve_state(str(bonding_curve))

        # Build buy transaction
        print(f"\nBuilding buy transaction for {amount_sol} SOL...")
        tx = await build_buy_transaction(
            payer=buyer_keypair,
            mint=mint,
            bonding_curve=bonding_curve,
            associated_bonding_curve=associated_bonding_curve,
            amount=amount_sol,
        )

        print("\nTransaction details:")
        print(f"Amount: {amount_sol} SOL")
        print(f"Buyer: {buyer_keypair.pubkey()}")
        print(f"Token Mint: {mint}")

        # Here you would sign and send the transaction
        # This is left as an exercise for actual implementation

    finally:
        await client.close()


async def example_sell_tokens(
    seller_keypair: Keypair,
    mint: Pubkey,
    bonding_curve: Pubkey,
    associated_bonding_curve: Pubkey,
    token_amount: float,
):
    """
    Example of selling tokens using the pump.fun protocol
    """
    client = SolanaClient()
    try:
        # First check the current state and price
        print(f"\nChecking current state for mint: {mint}")
        await process_bonding_curve_state(str(bonding_curve))

        # Build sell transaction
        print(f"\nBuilding sell transaction for {token_amount} tokens...")
        tx = await build_sell_transaction(
            payer=seller_keypair,
            mint=mint,
            bonding_curve=bonding_curve,
            associated_bonding_curve=associated_bonding_curve,
            amount=token_amount,
        )

        print("\nTransaction details:")
        print(f"Amount: {token_amount} tokens")
        print(f"Seller: {seller_keypair.pubkey()}")
        print(f"Token Mint: {mint}")

        # Here you would sign and send the transaction
        # This is left as an exercise for actual implementation

    finally:
        await client.close()


async def example_transactions():
    # Create test keypair (replace with your actual keypair)
    payer = Keypair()

    # Example addresses (replace with actual addresses)
    mint = Pubkey.new_unique()
    bonding_curve = Pubkey.new_unique()
    associated_bonding_curve = Pubkey.new_unique()

    # Build buy transaction (0.1 SOL amount)
    print("\n=== Building Buy Transaction ===")
    buy_amount = 0.1
    buy_tx = await build_buy_transaction(
        payer=payer,
        mint=mint,
        bonding_curve=bonding_curve,
        associated_bonding_curve=associated_bonding_curve,
        amount=buy_amount,
    )
    print(f"Buy transaction built for {buy_amount} SOL:")
    print(buy_tx)

    # Build sell transaction (100 token amount)
    print("\n=== Building Sell Transaction ===")
    sell_amount = 100
    sell_tx = await build_sell_transaction(
        payer=payer,
        mint=mint,
        bonding_curve=bonding_curve,
        associated_bonding_curve=associated_bonding_curve,
        amount=sell_amount,
    )
    print(f"Sell transaction built for {sell_amount} tokens:")
    print(sell_tx)


async def main():
    try:
        await example_transactions()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
