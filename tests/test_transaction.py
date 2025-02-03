import base64
import json
import os
from unittest.mock import Mock, patch

import pytest
from solders.keypair import Keypair
from solders.pubkey import Pubkey

from pumpfun_sdk.idl import load_pump_idl
from pumpfun_sdk.transaction import (
    AccountMeta,
    build_buy_transaction,
    build_sell_transaction,
    decode_transaction,
    get_instruction_discriminator,
    get_instruction_name,
    load_transaction,
)


@pytest.fixture
def mock_keypair():
    return Keypair()


@pytest.fixture
def mock_pubkey():
    return Pubkey.new_unique()


@pytest.fixture
def default_idl():
    return load_pump_idl()


@pytest.mark.asyncio
async def test_build_buy_transaction(mock_keypair, mock_pubkey):
    amount_sol = 0.1
    tx = await build_buy_transaction(
        payer=mock_keypair,
        mint=mock_pubkey,
        bonding_curve=mock_pubkey,
        associated_bonding_curve=mock_pubkey,
        amount=amount_sol,
    )
    assert tx is not None
    # Additional assertions can be added based on expected transaction structure


@pytest.mark.asyncio
async def test_build_sell_transaction(mock_keypair, mock_pubkey):
    token_amount = 100
    tx = await build_sell_transaction(
        payer=mock_keypair,
        mint=mock_pubkey,
        bonding_curve=mock_pubkey,
        associated_bonding_curve=mock_pubkey,
        amount=token_amount,
    )
    assert tx is not None


def test_get_instruction_discriminator():
    test_name = "test_instruction"
    discriminator = get_instruction_discriminator(test_name)
    assert len(discriminator) == 8
    # The function is deterministic
    assert get_instruction_discriminator(test_name) == discriminator


def test_get_instruction_name(default_idl):
    # Get a real instruction name from the default IDL
    instruction_name = default_idl["instructions"][0]["name"]
    discriminator = get_instruction_discriminator(instruction_name)
    mock_data = discriminator + b"additional_data"
    name = get_instruction_name(default_idl, mock_data)
    assert name == instruction_name


def test_get_instruction_name_unknown():
    mock_idl = {"instructions": []}
    mock_data = b"invalid_discriminator_data"
    name = get_instruction_name(mock_idl, mock_data)
    assert name == "unknown"


@pytest.mark.asyncio
async def test_account_meta_invalid_pubkey():
    invalid_pubkey = "not a pubkey"  # Not a Pubkey instance
    with pytest.raises(ValueError, match="Invalid pubkey"):
        AccountMeta(pubkey=invalid_pubkey, is_signer=False, is_writable=False)


@pytest.mark.asyncio
async def test_decode_transaction_invalid_data():
    mock_idl = {"instructions": []}
    invalid_data = {}  # Empty dict
    with pytest.raises(ValueError, match="Invalid transaction data"):
        decode_transaction(invalid_data, mock_idl)


@pytest.mark.asyncio
async def test_build_buy_transaction_zero_amount():
    key = Keypair()
    pub = Pubkey.new_unique()
    with pytest.raises(ValueError, match="Amount must be greater than 0"):
        await build_buy_transaction(
            payer=key,
            mint=pub,
            bonding_curve=pub,
            associated_bonding_curve=pub,
            amount=0,
        )


def test_decode_transaction_with_instructions(default_idl):
    mock_tx_data = {"transaction": [base64.b64encode(b"test_data").decode("utf-8")]}

    with patch(
        "solders.transaction.VersionedTransaction.from_bytes"
    ) as mock_from_bytes:
        mock_instruction = Mock()
        mock_instruction.data = b"test_instruction_data"
        mock_instruction.program_id_index = 0
        mock_instruction.accounts = [0]
        mock_transaction = Mock()
        mock_transaction.message.instructions = [mock_instruction]
        mock_transaction.message.account_keys = [Pubkey.new_unique()]
        mock_from_bytes.return_value = mock_transaction

        result = decode_transaction(mock_tx_data, default_idl)
        assert isinstance(result, list)
        assert len(result) > 0
        assert "programId" in result[0]
        assert "instruction_name" in result[0]
        assert "data" in result[0]
        assert "accounts" in result[0]


@pytest.mark.asyncio
async def test_build_sell_transaction_zero_amount():
    key = Keypair()
    pub = Pubkey.new_unique()
    with pytest.raises(ValueError, match="Amount must be greater than 0"):
        await build_sell_transaction(
            payer=key,
            mint=pub,
            bonding_curve=pub,
            associated_bonding_curve=pub,
            amount=0,
        )


def test_account_meta_to_solders():
    pubkey = Pubkey.new_unique()
    account_meta = AccountMeta(pubkey=pubkey, is_signer=True, is_writable=True)
    solders_meta = account_meta.to_solders()
    assert solders_meta.pubkey == pubkey
    assert solders_meta.is_signer is True
    assert solders_meta.is_writable is True


def test_account_meta_to_solders_error():
    # Test with an invalid pubkey object that is not an instance of Pubkey.
    class FakePubkey:
        pass

    fake_pubkey = FakePubkey()
    with pytest.raises(ValueError, match="Invalid pubkey"):
        AccountMeta(pubkey=fake_pubkey, is_signer=True, is_writable=True)


def test_load_transaction(tmp_path):
    # Write a temporary JSON file with dummy transaction data.
    data = {"transaction": ["dummy"]}
    file_path = tmp_path / "tx.json"
    file_path.write_text(json.dumps(data))
    loaded = load_transaction(str(file_path))
    assert loaded == data


def test_decode_transaction_without_idl():
    # Test transaction decoding when no IDL is provided.
    mock_tx_data = {"transaction": [base64.b64encode(b"test_data").decode("utf-8")]}
    with patch(
        "solders.transaction.VersionedTransaction.from_bytes"
    ) as mock_from_bytes:
        mock_instruction = Mock()
        mock_instruction.data = b"test_instruction_data"
        mock_instruction.program_id_index = 0
        mock_instruction.accounts = [0]
        mock_transaction = Mock()
        mock_transaction.message.instructions = [mock_instruction]
        mock_transaction.message.account_keys = [Pubkey.new_unique()]
        mock_from_bytes.return_value = mock_transaction

        result = decode_transaction(mock_tx_data)  # idl is None
        assert isinstance(result, list)
        assert len(result) > 0
        # Since no IDL is provided, the instruction_name should default to "unknown"
        assert result[0]["instruction_name"] == "unknown"
