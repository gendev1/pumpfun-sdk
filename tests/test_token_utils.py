import types
from solders.pubkey import Pubkey

from pumpfun_sdk.usecases.token import _get_transaction_type
from pumpfun_sdk.config import (
    BUY_DISCRIMINATOR,
    SELL_DISCRIMINATOR,
    PUMP_PROGRAM,
)


def make_tx(discriminator: bytes) -> types.SimpleNamespace:
    instruction = types.SimpleNamespace(
        program_id=PUMP_PROGRAM,
        data=discriminator,
    )
    message = types.SimpleNamespace(
        instructions=[instruction],
        account_keys=[Pubkey.new_unique()],
    )
    tx = types.SimpleNamespace(transaction=types.SimpleNamespace(message=message))
    return tx


def test_get_transaction_type_buy():
    tx = make_tx(BUY_DISCRIMINATOR)
    assert _get_transaction_type(tx) == "buy"


def test_get_transaction_type_sell():
    tx = make_tx(SELL_DISCRIMINATOR)
    assert _get_transaction_type(tx) == "sell"


def test_get_transaction_type_other():
    tx = make_tx(b"randomdata")
    assert _get_transaction_type(tx) == "other"
