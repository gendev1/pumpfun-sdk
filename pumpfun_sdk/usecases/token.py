from typing import Dict, List, Optional

from solders.pubkey import Pubkey

from pumpfun_sdk.analytics import analyze_curve_state
from pumpfun_sdk.client import SolanaClient
from pumpfun_sdk.config import (
    BUY_DISCRIMINATOR,
    LAMPORTS_PER_SOL,
    PUMP_PROGRAM,
    SELL_DISCRIMINATOR,
    TOKEN_DECIMALS,
)
from pumpfun_sdk.pump_curve import BondingCurveState, calculate_bonding_curve_price


async def get_token_info(mint_address: str) -> Dict:
    """
    Get comprehensive token information including name, description, market cap,
    bonding curve progress, king of hill progress, and token creator.

    Args:
        mint_address (str): The token's mint address

    Returns:
        Dict: Token information including metadata and on-chain state
    """
    client = SolanaClient()
    try:
        # Get token metadata
        metadata_account = await client.get_token_metadata(mint_address)

        # Get bonding curve state
        bonding_curve = await client.get_bonding_curve(mint_address)
        curve_state = BondingCurveState(bonding_curve)

        # Calculate market cap
        price = calculate_bonding_curve_price(curve_state)
        market_cap = price * (curve_state.real_token_reserves / 10**TOKEN_DECIMALS)

        # Calculate bonding curve progress
        total_supply = curve_state.token_total_supply / 10**TOKEN_DECIMALS
        minted_supply = curve_state.real_token_reserves / 10**TOKEN_DECIMALS
        curve_progress = (minted_supply / total_supply) * 100 if total_supply > 0 else 0

        return {
            "name": metadata_account.data.name,
            "symbol": metadata_account.data.symbol,
            "description": metadata_account.data.uri,
            "creator": str(metadata_account.update_authority),
            "market_cap": market_cap,
            "curve_progress": curve_progress,
            "is_complete": curve_state.complete,
            "total_supply": total_supply,
            "minted_supply": minted_supply,
        }
    finally:
        await client.close()


async def get_token_price(mint_address: str) -> float:
    """
    Get current token price based on bonding curve state.

    Args:
        mint_address (str): The token's mint address

    Returns:
        float: Current token price in SOL
    """
    client = SolanaClient()
    try:
        bonding_curve = await client.get_bonding_curve(mint_address)
        curve_state = BondingCurveState(bonding_curve)
        return calculate_bonding_curve_price(curve_state)
    finally:
        await client.close()


async def get_token_holders(mint_address: str) -> List[Dict]:
    """
    Get list of token holders and their balances.

    Args:
        mint_address (str): The token's mint address

    Returns:
        List[Dict]: List of token holders with their balances
    """
    client = SolanaClient()
    try:
        # Get all token accounts for this mint
        token_accounts = await client.get_token_accounts_by_mint(mint_address)

        holders = []
        for account in token_accounts:
            balance = account.data.amount / 10**TOKEN_DECIMALS
            if balance > 0:
                holders.append({"address": str(account.pubkey), "balance": balance})

        # Sort by balance descending
        return sorted(holders, key=lambda x: x["balance"], reverse=True)
    finally:
        await client.close()


async def get_token_transactions(
    mint_address: str, limit: int = 100, before: Optional[str] = None
) -> List[Dict]:
    """
    Get token transaction history.

    Args:
        mint_address (str): The token's mint address
        limit (int): Maximum number of transactions to return
        before (Optional[str]): Transaction signature to fetch transactions before

    Returns:
        List[Dict]: List of token transactions
    """
    client = SolanaClient()
    try:
        # Get transaction signatures
        signatures = await client.get_signatures_for_address(
            Pubkey.from_string(mint_address), before=before, limit=limit
        )

        transactions = []
        for sig in signatures:
            tx = await client.get_parsed_transaction(sig.signature)
            if tx and tx.meta:
                # Extract relevant transaction info
                transactions.append(
                    {
                        "signature": sig.signature,
                        "block_time": tx.block_time,
                        "success": not tx.meta.err,
                        "fee": tx.meta.fee / LAMPORTS_PER_SOL,
                        "type": _get_transaction_type(tx),
                    }
                )

        return transactions
    finally:
        await client.close()


async def get_token_liquidity(mint_address: str) -> Dict:
    """
    Get token liquidity information.

    Args:
        mint_address (str): The token's mint address

    Returns:
        Dict: Liquidity information including SOL and token reserves
    """
    client = SolanaClient()
    try:
        bonding_curve = await client.get_bonding_curve(mint_address)
        curve_state = BondingCurveState(bonding_curve)

        return {
            "sol_reserves": curve_state.real_sol_reserves / LAMPORTS_PER_SOL,
            "token_reserves": curve_state.real_token_reserves / 10**TOKEN_DECIMALS,
            "virtual_sol_reserves": curve_state.virtual_sol_reserves / LAMPORTS_PER_SOL,
            "virtual_token_reserves": curve_state.virtual_token_reserves
            / 10**TOKEN_DECIMALS,
        }
    finally:
        await client.close()


def _get_transaction_type(tx) -> str:
    """Helper function to determine transaction type."""
    if not tx.transaction.message.instructions:
        return "unknown"

    program_id = str(tx.transaction.message.instructions[0].program_id)
    if program_id == str(PUMP_PROGRAM):  # Use PUMP_PROGRAM from config
        instruction_data = tx.transaction.message.instructions[0].data
        if instruction_data.startswith(
            BUY_DISCRIMINATOR
        ):  # Use BUY_DISCRIMINATOR from config
            return "buy"
        elif instruction_data.startswith(
            SELL_DISCRIMINATOR
        ):  # Use SELL_DISCRIMINATOR from config
            return "sell"

    return "other"
