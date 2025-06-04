import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, Mock

from pumpfun_sdk.config import LAMPORTS_PER_SOL, TOKEN_DECIMALS

import pytest

from pumpfun_sdk.usecases.token import (
    get_token_info,
    get_token_price,
    get_token_holders,
    get_token_transactions,
    get_token_liquidity,
)


def run(coro):
    """Helper to run async coroutines in tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


class DummyMeta:
    def __init__(self):
        self.err = None
        self.fee = 5000


class DummyTransaction:
    def __init__(self):
        self.block_time = 123
        self.meta = DummyMeta()
        self.transaction = SimpleNamespace(message=SimpleNamespace(instructions=[]))


@pytest.fixture
def mock_client():
    with patch("pumpfun_sdk.usecases.token.SolanaClient") as MockClient:
        instance = MockClient.return_value
        instance.close = AsyncMock()
        yield instance
        run(instance.close())


@pytest.fixture
def mock_curve_state():
    state = SimpleNamespace(
        real_token_reserves=10 ** TOKEN_DECIMALS,
        real_sol_reserves=2 * LAMPORTS_PER_SOL,
        token_total_supply=10 ** TOKEN_DECIMALS,
        virtual_sol_reserves=3 * LAMPORTS_PER_SOL,
        virtual_token_reserves=int(1.5 * 10 ** TOKEN_DECIMALS),
        complete=False,
    )
    return state


def setup_curve_mocks(mock_client, mock_curve_state):
    mock_client.get_bonding_curve = AsyncMock(return_value=b"curve_bytes")
    patch_state = patch(
        "pumpfun_sdk.usecases.token.BondingCurveState",
        return_value=mock_curve_state,
    )
    patch_price = patch(
        "pumpfun_sdk.usecases.token.calculate_bonding_curve_price",
        return_value=1.23,
    )
    return patch_state, patch_price


def test_get_token_price(mock_client, mock_curve_state):
    patch_state, patch_price = setup_curve_mocks(mock_client, mock_curve_state)
    with patch_state as _state, patch_price as mock_price:
        result = run(get_token_price("mint"))
        assert result == 1.23
        mock_client.get_bonding_curve.assert_awaited_once_with("mint")
        mock_price.assert_called_once()


def test_get_token_info(mock_client, mock_curve_state):
    meta = SimpleNamespace(
        data=SimpleNamespace(name="n", symbol="s", uri="u"),
        update_authority=Mock(return_value="auth"),
    )
    mock_client.get_token_metadata = AsyncMock(return_value=meta)
    patch_state, patch_price = setup_curve_mocks(mock_client, mock_curve_state)
    with patch_state, patch_price:
        info = run(get_token_info("mint"))
        assert info["name"] == "n"
        assert info["symbol"] == "s"
        assert "market_cap" in info


def test_get_token_holders(mock_client):
    account = SimpleNamespace(pubkey="addr", data=SimpleNamespace(amount=2000000))
    mock_client.get_token_accounts_by_mint = AsyncMock(return_value=[account])
    holders = run(get_token_holders("mint"))
    assert holders == [{"address": "addr", "balance": 2.0}]


def test_get_token_transactions(mock_client):
    sig = SimpleNamespace(signature="sig")
    mock_client.get_signatures_for_address = AsyncMock(return_value=[sig])
    tx = DummyTransaction()
    mock_client.get_parsed_transaction = AsyncMock(return_value=tx)
    with patch("pumpfun_sdk.usecases.token._get_transaction_type", return_value="buy"), \
         patch("pumpfun_sdk.usecases.token.Pubkey.from_string", return_value="key"):
        txs = run(get_token_transactions("mint"))
        assert txs[0]["signature"] == "sig"
        assert txs[0]["fee"] == 0.000005


def test_get_token_liquidity(mock_client, mock_curve_state):
    patch_state, patch_price = setup_curve_mocks(mock_client, mock_curve_state)
    with patch_state, patch_price:
        info = run(get_token_liquidity("mint"))
        assert info["sol_reserves"] == 2.0
        assert info["token_reserves"] == 1.0
