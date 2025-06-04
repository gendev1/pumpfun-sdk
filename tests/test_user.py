import types
from solders.pubkey import Pubkey

from pumpfun_sdk.usecases.user import _extract_mint_address


def make_tx(mint_index: int, account_keys_count: int = 5):
    """Create a minimal mock transaction structure."""
    tx = types.SimpleNamespace()
    message = types.SimpleNamespace()
    instruction = types.SimpleNamespace()

    # Accounts list must be at least 4 long. The 4th entry (index 3) is the
    # mint account index that the helper will look up. Fill in dummy indices for
    # the rest.
    accounts = [0, 1, 2, mint_index]
    instruction.accounts = accounts

    message.instructions = [instruction]
    message.account_keys = [Pubkey.new_unique() for _ in range(account_keys_count)]
    tx.transaction = types.SimpleNamespace(message=message)
    return tx


def test_extract_mint_address_ok():
    tx = make_tx(3)
    expected = str(tx.transaction.message.account_keys[3])
    assert _extract_mint_address(tx) == expected


def test_extract_mint_address_missing_instruction():
    tx = types.SimpleNamespace(
        transaction=types.SimpleNamespace(
            message=types.SimpleNamespace(instructions=[])
        )
    )
    assert _extract_mint_address(tx) is None


def test_extract_mint_address_out_of_bounds():
    tx = make_tx(10, account_keys_count=5)
    assert _extract_mint_address(tx) is None


from pumpfun_sdk.config import (
    BUY_DISCRIMINATOR,
    SELL_DISCRIMINATOR,
    CREATE_DISCRIMINATOR,
    LAMPORTS_PER_SOL,
    TOKEN_DECIMALS,
    PUMP_PROGRAM,
)
from pumpfun_sdk.usecases.user import (
    _extract_buy_amounts,
    _extract_sell_amounts,
    _is_buy_tx,
    _is_sell_tx,
    _is_token_creation_tx,
    _get_transaction_type,
)


def make_basic_tx(discriminator: bytes, amount: int = 0, mint_index: int = 3):
    instr_data = bytearray(discriminator)
    instr_data.extend(amount.to_bytes(8, "little"))
    instruction = types.SimpleNamespace(
        program_id=PUMP_PROGRAM,
        data=bytes(instr_data),
        accounts=[0, 1, 2, mint_index],
    )
    message = types.SimpleNamespace(
        instructions=[instruction],
        account_keys=[Pubkey.new_unique() for _ in range(5)],
    )
    meta = types.SimpleNamespace(
        pre_balances=[100_000_000_000], post_balances=[90_000_000_000]
    )
    tx = types.SimpleNamespace(
        transaction=types.SimpleNamespace(message=message), meta=meta
    )
    return tx


def test_is_token_creation_tx():
    tx = make_basic_tx(CREATE_DISCRIMINATOR)
    assert _is_token_creation_tx(tx)


def test_is_buy_tx():
    tx = make_basic_tx(BUY_DISCRIMINATOR)
    assert _is_buy_tx(tx)


def test_is_sell_tx():
    tx = make_basic_tx(SELL_DISCRIMINATOR)
    assert _is_sell_tx(tx)


def test_extract_buy_amounts():
    amount = 5 * LAMPORTS_PER_SOL
    tx = make_basic_tx(BUY_DISCRIMINATOR, amount)
    token_amount, sol_spent = _extract_buy_amounts(tx)
    assert token_amount == 5.0
    assert sol_spent == 10.0  # difference between pre and post balances


def test_extract_sell_amounts():
    amount = 7 * 10**TOKEN_DECIMALS
    tx = make_basic_tx(SELL_DISCRIMINATOR, amount)
    tx.meta.pre_balances[0] = 90_000_000_000
    tx.meta.post_balances[0] = 95_000_000_000
    token_amount, sol_received = _extract_sell_amounts(tx)
    assert token_amount == 7.0
    assert sol_received == 5.0


def test_get_transaction_type_variants():
    tx_buy = make_basic_tx(BUY_DISCRIMINATOR)
    assert _get_transaction_type(tx_buy) == "buy"
    tx_sell = make_basic_tx(SELL_DISCRIMINATOR)
    assert _get_transaction_type(tx_sell) == "sell"
    tx_create = make_basic_tx(CREATE_DISCRIMINATOR)
    assert _get_transaction_type(tx_create) == "create"
    tx_other = make_basic_tx(b"randomdata")
    assert _get_transaction_type(tx_other) == "other"
