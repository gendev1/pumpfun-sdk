from unittest.mock import Mock, patch

import pytest
from solana.rpc.async_api import AsyncClient

from pumpfun_sdk.client import SolanaClient
from pumpfun_sdk.config import RPC_ENDPOINT


@pytest.mark.asyncio
async def test_client_initialization():
    client = SolanaClient()
    assert client.endpoint == RPC_ENDPOINT
    assert isinstance(client.client, AsyncClient)
    await client.close()


@pytest.mark.asyncio
async def test_get_account_info():
    with patch("solana.rpc.async_api.AsyncClient.get_account_info") as mock_get_account:
        # Setup mock response
        mock_response = Mock()
        mock_response.value = Mock()
        mock_response.value.data = b"test_data"
        mock_get_account.return_value = mock_response

        client = SolanaClient()
        try:
            result = await client.get_account_info("test_address")
            assert result.data == b"test_data"
            mock_get_account.assert_called_once_with("test_address")
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_get_account_info_no_data():
    with patch("solana.rpc.async_api.AsyncClient.get_account_info") as mock_get_account:
        # Setup mock response with no data
        mock_response = Mock()
        mock_response.value = None
        mock_get_account.return_value = mock_response

        client = SolanaClient()
        try:
            with pytest.raises(
                ValueError, match="No data found for account test_address"
            ):
                await client.get_account_info("test_address")
        finally:
            await client.close()
