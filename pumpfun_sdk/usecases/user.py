# TODO: Get user created tokens

# TODO: Get user bought tokens

# TODO: Get user sold tokens

# TODO: Get user liquidity

# TODO: Get user transactions

from typing import Dict, List, Optional

from solders.pubkey import Pubkey

from pumpfun_sdk.analytics import analyze_curve_state
from pumpfun_sdk.client import SolanaClient
from pumpfun_sdk.config import (
    BUY_DISCRIMINATOR,
    CREATE_DISCRIMINATOR,
    INITIALIZE_DISCRIMINATOR,
    LAMPORTS_PER_SOL,
    PUMP_PROGRAM,
    SELL_DISCRIMINATOR,
    SET_PARAMS_DISCRIMINATOR,
    TOKEN_DECIMALS,
    WITHDRAW_DISCRIMINATOR,
)
from pumpfun_sdk.pump_curve import BondingCurveState, calculate_bonding_curve_price

from .token import get_token_info, get_token_price


async def get_user_created_tokens(user_address: str) -> List[Dict]:
    """
    Get all tokens created by a specific user.

    Args:
        user_address (str): The user's wallet address

    Returns:
        List[Dict]: List of tokens created by the user with their details
    """
    client = SolanaClient()
    try:
        # Get all token creation events for this user
        signatures = await client.get_signatures_for_address(
            Pubkey.from_string(user_address), limit=1000  # Adjust limit as needed
        )

        created_tokens = []
        for sig in signatures:
            tx = await client.get_parsed_transaction(sig.signature)
            if tx and tx.meta and not tx.meta.err:
                # Check if this is a token creation transaction
                if _is_token_creation_tx(tx):
                    # Extract mint address from the transaction
                    mint_address = _extract_mint_address(tx)
                    if mint_address:
                        # Get token details
                        token_info = await get_token_info(mint_address)
                        token_info["created_at"] = tx.block_time
                        created_tokens.append(token_info)

        return created_tokens
    finally:
        await client.close()


async def get_user_bought_tokens(user_address: str) -> List[Dict]:
    """
    Get all tokens bought by a specific user.

    Args:
        user_address (str): The user's wallet address

    Returns:
        List[Dict]: List of tokens bought by the user with amounts and prices
    """
    client = SolanaClient()
    try:
        # Get all buy transactions for this user
        signatures = await client.get_signatures_for_address(
            Pubkey.from_string(user_address), limit=1000  # Adjust limit as needed
        )

        bought_tokens = {}
        for sig in signatures:
            tx = await client.get_parsed_transaction(sig.signature)
            if tx and tx.meta and not tx.meta.err:
                # Check if this is a buy transaction
                if _is_buy_tx(tx):
                    mint_address = _extract_mint_address(tx)
                    if mint_address:
                        if mint_address not in bought_tokens:
                            # Initialize token entry
                            token_info = await get_token_info(mint_address)
                            bought_tokens[mint_address] = {
                                "token_info": token_info,
                                "total_amount": 0,
                                "total_sol_spent": 0,
                                "transactions": [],
                            }

                        # Extract transaction details
                        amount, sol_spent = _extract_buy_amounts(tx)
                        bought_tokens[mint_address]["total_amount"] += amount
                        bought_tokens[mint_address]["total_sol_spent"] += sol_spent
                        bought_tokens[mint_address]["transactions"].append(
                            {
                                "signature": sig.signature,
                                "amount": amount,
                                "sol_spent": sol_spent,
                                "timestamp": tx.block_time,
                            }
                        )

        return list(bought_tokens.values())
    finally:
        await client.close()


async def get_user_sold_tokens(user_address: str) -> List[Dict]:
    """
    Get all tokens sold by a specific user.

    Args:
        user_address (str): The user's wallet address

    Returns:
        List[Dict]: List of tokens sold by the user with amounts and prices
    """
    client = SolanaClient()
    try:
        # Get all sell transactions for this user
        signatures = await client.get_signatures_for_address(
            Pubkey.from_string(user_address), limit=1000  # Adjust limit as needed
        )

        sold_tokens = {}
        for sig in signatures:
            tx = await client.get_parsed_transaction(sig.signature)
            if tx and tx.meta and not tx.meta.err:
                # Check if this is a sell transaction
                if _is_sell_tx(tx):
                    mint_address = _extract_mint_address(tx)
                    if mint_address:
                        if mint_address not in sold_tokens:
                            # Initialize token entry
                            token_info = await get_token_info(mint_address)
                            sold_tokens[mint_address] = {
                                "token_info": token_info,
                                "total_amount": 0,
                                "total_sol_received": 0,
                                "transactions": [],
                            }

                        # Extract transaction details
                        amount, sol_received = _extract_sell_amounts(tx)
                        sold_tokens[mint_address]["total_amount"] += amount
                        sold_tokens[mint_address]["total_sol_received"] += sol_received
                        sold_tokens[mint_address]["transactions"].append(
                            {
                                "signature": sig.signature,
                                "amount": amount,
                                "sol_received": sol_received,
                                "timestamp": tx.block_time,
                            }
                        )

        return list(sold_tokens.values())
    finally:
        await client.close()


async def get_user_liquidity(user_address: str) -> List[Dict]:
    """
    Get user's liquidity positions across all tokens.

    Args:
        user_address (str): The user's wallet address

    Returns:
        List[Dict]: List of user's liquidity positions with token details
    """
    client = SolanaClient()
    try:
        # Get all token accounts owned by the user
        token_accounts = await client.get_token_accounts_by_owner(user_address)

        liquidity_positions = []
        for account in token_accounts:
            balance = account.data.amount / 10**TOKEN_DECIMALS
            if balance > 0:
                try:
                    # Get token details and current price
                    token_info = await get_token_info(str(account.data.mint))
                    current_price = await get_token_price(str(account.data.mint))

                    liquidity_positions.append(
                        {
                            "token_info": token_info,
                            "balance": balance,
                            "current_price": current_price,
                            "value_in_sol": balance * current_price,
                        }
                    )
                except Exception:
                    # Skip tokens that aren't pump tokens
                    continue

        # Sort by value in SOL descending
        return sorted(
            liquidity_positions, key=lambda x: x["value_in_sol"], reverse=True
        )
    finally:
        await client.close()


async def get_user_transactions(
    user_address: str, limit: int = 100, before: Optional[str] = None
) -> List[Dict]:
    """
    Get all pump-related transactions for a user.

    Args:
        user_address (str): The user's wallet address
        limit (int): Maximum number of transactions to return
        before (Optional[str]): Transaction signature to fetch transactions before

    Returns:
        List[Dict]: List of user's transactions with details
    """
    client = SolanaClient()
    try:
        signatures = await client.get_signatures_for_address(
            Pubkey.from_string(user_address), before=before, limit=limit
        )

        transactions = []
        for sig in signatures:
            tx = await client.get_parsed_transaction(sig.signature)
            if tx and tx.meta:
                # Check if this is a pump transaction
                tx_type = _get_transaction_type(tx)
                if tx_type != "other":
                    mint_address = _extract_mint_address(tx)
                    if mint_address:
                        token_info = await get_token_info(mint_address)

                        # Extract amounts based on transaction type
                        if tx_type == "buy":
                            amount, sol_amount = _extract_buy_amounts(tx)
                        elif tx_type == "sell":
                            amount, sol_amount = _extract_sell_amounts(tx)
                        else:  # create
                            amount = sol_amount = 0

                        transactions.append(
                            {
                                "signature": sig.signature,
                                "block_time": tx.block_time,
                                "success": not tx.meta.err,
                                "type": tx_type,
                                "token_info": token_info,
                                "amount": amount,
                                "sol_amount": sol_amount,
                                "fee": tx.meta.fee / LAMPORTS_PER_SOL,
                            }
                        )

        return transactions
    finally:
        await client.close()


def _is_token_creation_tx(tx) -> bool:
    """Check if transaction is a token creation transaction."""
    if not tx.transaction.message.instructions:
        return False

    program_id = str(tx.transaction.message.instructions[0].program_id)
    if program_id == str(PUMP_PROGRAM):
        instruction_data = tx.transaction.message.instructions[0].data
        return instruction_data.startswith(CREATE_DISCRIMINATOR)
    return False


def _is_buy_tx(tx) -> bool:
    """Check if transaction is a buy transaction."""
    if not tx.transaction.message.instructions:
        return False

    program_id = str(tx.transaction.message.instructions[0].program_id)
    if program_id == str(PUMP_PROGRAM):
        instruction_data = tx.transaction.message.instructions[0].data
        return instruction_data.startswith(BUY_DISCRIMINATOR)
    return False


def _is_sell_tx(tx) -> bool:
    """Check if transaction is a sell transaction."""
    if not tx.transaction.message.instructions:
        return False

    program_id = str(tx.transaction.message.instructions[0].program_id)
    if program_id == str(PUMP_PROGRAM):
        instruction_data = tx.transaction.message.instructions[0].data
        return instruction_data.startswith(SELL_DISCRIMINATOR)
    return False


def _extract_mint_address(tx) -> Optional[str]:
    """Extract mint address from transaction."""
    try:
        for account in tx.transaction.message.account_keys:
            # The mint account is typically the 4th account in pump transactions
            if account.signer == False and account.writable == True:
                return str(account.pubkey)
    except Exception:
        return None


def _extract_buy_amounts(tx) -> tuple[float, float]:
    """Extract token amount and SOL spent from buy transaction."""
    try:
        # Extract from transaction data
        instruction_data = tx.transaction.message.instructions[0].data
        amount_lamports = int.from_bytes(instruction_data[8:16], "little")
        token_amount = amount_lamports / LAMPORTS_PER_SOL
        sol_spent = tx.meta.pre_balances[0] - tx.meta.post_balances[0]
        return token_amount, sol_spent / LAMPORTS_PER_SOL
    except Exception:
        return 0.0, 0.0


def _extract_sell_amounts(tx) -> tuple[float, float]:
    """Extract token amount and SOL received from sell transaction."""
    try:
        # Extract from transaction data
        instruction_data = tx.transaction.message.instructions[0].data
        token_amount = (
            int.from_bytes(instruction_data[8:16], "little") / 10**TOKEN_DECIMALS
        )
        sol_received = tx.meta.post_balances[0] - tx.meta.pre_balances[0]
        return token_amount, sol_received / LAMPORTS_PER_SOL
    except Exception:
        return 0.0, 0.0


def _get_transaction_type(tx) -> str:
    """Helper function to determine transaction type."""
    if not tx.transaction.message.instructions:
        return "unknown"

    program_id = str(tx.transaction.message.instructions[0].program_id)
    if program_id == str(PUMP_PROGRAM):
        instruction_data = tx.transaction.message.instructions[0].data
        if instruction_data.startswith(BUY_DISCRIMINATOR):
            return "buy"
        elif instruction_data.startswith(SELL_DISCRIMINATOR):
            return "sell"
        elif instruction_data.startswith(CREATE_DISCRIMINATOR):
            return "create"
        elif instruction_data.startswith(INITIALIZE_DISCRIMINATOR):
            return "initialize"
        elif instruction_data.startswith(SET_PARAMS_DISCRIMINATOR):
            return "set_params"
        elif instruction_data.startswith(WITHDRAW_DISCRIMINATOR):
            return "withdraw"

    return "other"
