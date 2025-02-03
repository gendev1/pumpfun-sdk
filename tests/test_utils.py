import asyncio
import json
from unittest.mock import AsyncMock, Mock, mock_open, patch

import pytest

from pumpfun_sdk.idl import load_pump_idl
from pumpfun_sdk.utils import (
    decode_transaction_from_file,
    dummy_event_handler,
    example_subscribe_to_logs,
    monitor_new_tokens,
    process_block_data,
    process_bonding_curve_state,
    subscribe_to_events,
)


@pytest.fixture
def mock_idl():
    return {"version": "0.1.0", "name": "test_program", "instructions": []}


@pytest.fixture
def mock_idl_file(tmp_path):
    idl_data = {"version": "0.1.0", "name": "test_program", "instructions": []}
    file_path = tmp_path / "test_idl.json"
    file_path.write_text(json.dumps(idl_data))
    return file_path


@pytest.mark.asyncio
async def test_subscribe_to_events():
    mock_callback = AsyncMock()

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        # Set up recv to return one message then raise an exception to break the loop
        mock_ws.recv = AsyncMock(
            side_effect=[
                '{"result": {"value": {"logs": ["test log"]}}}',
                asyncio.CancelledError,  # This will break the loop
            ]
        )
        mock_connect.return_value = mock_ws

        task = asyncio.create_task(
            subscribe_to_events(
                program_id="test_program",
                callback=mock_callback,
                subscription_type="logs",
            )
        )

        # Wait a short time for the callback to be called
        await asyncio.sleep(0.1)

        # Cancel and cleanup
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

        # Verify the callback was called
        assert mock_callback.call_count >= 1


@pytest.mark.asyncio
async def test_subscribe_to_events_invalid_type():
    mock_callback = AsyncMock()
    # Don't need to mock websockets since it should fail before connection
    with pytest.raises(ValueError, match="Unknown subscription type"):
        # Use a timeout to prevent infinite loop
        async with asyncio.timeout(1.0):
            await subscribe_to_events(
                program_id="test_program",
                callback=mock_callback,
                subscription_type="invalid",
            )


@pytest.mark.asyncio
async def test_process_bonding_curve_state():
    mock_account_info = Mock()
    # Create valid bonding curve data
    from pumpfun_sdk.config import EXPECTED_DISCRIMINATOR

    data = bytearray(EXPECTED_DISCRIMINATOR)
    data.extend((100).to_bytes(8, "little"))  # virtual_token_reserves
    data.extend((200).to_bytes(8, "little"))  # virtual_sol_reserves
    data.extend((300).to_bytes(8, "little"))  # real_token_reserves
    data.extend((400).to_bytes(8, "little"))  # real_sol_reserves
    data.extend((500).to_bytes(8, "little"))  # token_total_supply
    data.extend((1).to_bytes(1, "little"))  # complete flag
    mock_account_info.data = bytes(data)

    with patch("pumpfun_sdk.client.SolanaClient.get_account_info") as mock_get_account:
        mock_get_account.return_value = mock_account_info

        result = await process_bonding_curve_state("test_address")
        assert isinstance(result, dict)  # Result should be the analysis dict
        assert "price_sol" in result
        assert "virtual_token_reserves" in result
        mock_get_account.assert_called_once_with("test_address")


@pytest.mark.asyncio
async def test_process_bonding_curve_state_invalid_data():
    with patch("pumpfun_sdk.client.SolanaClient.get_account_info") as mock_get_account:
        mock_account_info = Mock()
        mock_account_info.data = b"invalid_data"
        mock_get_account.return_value = mock_account_info

        with pytest.raises(
            ValueError, match="Invalid bonding curve data: Invalid discriminator"
        ):
            await process_bonding_curve_state("test_address")


@pytest.mark.asyncio
async def test_websocket_connection_error():
    mock_callback = AsyncMock()
    with patch("websockets.connect", side_effect=Exception("Connection failed")):
        with pytest.raises(Exception, match="Connection failed"):
            await subscribe_to_events(program_id="test_program", callback=mock_callback)


@pytest.mark.asyncio
async def test_monitor_new_tokens():
    mock_callback = AsyncMock()

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        # Set up recv to return one message then raise an exception to break the loop
        mock_ws.recv = AsyncMock(
            side_effect=[
                '{"result": {"value": {"logs": ["Program log: Instruction: Create"]}}}',
                asyncio.CancelledError,  # This will break the loop
            ]
        )
        mock_connect.return_value = mock_ws

        task = asyncio.create_task(monitor_new_tokens(callback=mock_callback))

        # Wait a short time for the callback to be called
        await asyncio.sleep(0.1)

        # Cancel and cleanup
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

        # Verify the callback was called
        assert mock_callback.call_count >= 1


@pytest.mark.asyncio
async def test_dummy_event_handler(capsys):
    test_data = {"test": "data"}
    await dummy_event_handler(test_data)
    captured = capsys.readouterr()
    assert "Received event:" in captured.out
    assert "test" in captured.out


@pytest.mark.asyncio
async def test_example_subscribe_to_logs():
    with patch("pumpfun_sdk.utils.subscribe_to_events") as mock_subscribe:
        mock_subscribe.return_value = None
        await example_subscribe_to_logs("test_program")
        mock_subscribe.assert_called_once()


@pytest.mark.asyncio
async def test_decode_transaction_from_file():
    mock_tx_data = {"test": "data"}

    with patch("pumpfun_sdk.utils.load_transaction") as mock_load_tx, patch(
        "pumpfun_sdk.utils.decode_transaction"
    ) as mock_decode:
        mock_load_tx.return_value = mock_tx_data
        mock_decode.return_value = [{"instruction": "test"}]

        # Test without custom IDL file
        await decode_transaction_from_file("test.json")
        mock_load_tx.assert_called_once()
        mock_decode.assert_called_once()

        # Test with custom IDL file
        mock_load_tx.reset_mock()
        mock_decode.reset_mock()

        with patch(
            "builtins.open", new_callable=mock_open, read_data='{"custom": "idl"}'
        ):
            await decode_transaction_from_file("test.json", "custom_idl.json")
            mock_load_tx.assert_called_once()
            mock_decode.assert_called_once()


@pytest.mark.asyncio
async def test_process_block_data():
    mock_callback = AsyncMock()
    test_data = {"result": {"value": {"test": "data"}}}
    await process_block_data(test_data, mock_callback)
    mock_callback.assert_called_once_with({"test": "data"})


@pytest.mark.asyncio
async def test_subscribe_to_events_send_error():
    mock_callback = AsyncMock()

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock(side_effect=Exception("Send failed"))
        mock_connect.return_value = mock_ws

        with pytest.raises(Exception, match="Send failed"):
            await subscribe_to_events(program_id="test_program", callback=mock_callback)


@pytest.mark.asyncio
async def test_monitor_new_tokens_send_error():
    mock_callback = AsyncMock()

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock(side_effect=Exception("Send failed"))
        mock_connect.return_value = mock_ws

        with pytest.raises(Exception, match="Send failed"):
            await monitor_new_tokens(callback=mock_callback)


@pytest.mark.asyncio
async def test_subscribe_to_events_unknown_type_in_request():
    mock_callback = AsyncMock()

    # We expect the function to raise ValueError before attempting to connect,
    # because 'other' is not a supported subscription type.
    with pytest.raises(ValueError, match="Unknown subscription type"):
        await subscribe_to_events(
            program_id="test_program",
            callback=mock_callback,
            subscription_type="other",  # Not in ['account', 'logs']
        )


@pytest.mark.asyncio
async def test_monitor_new_tokens_callback_error():
    # Test the case where callback raises an error
    async def error_callback(data):
        raise Exception("Callback error")

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        mock_ws.recv = AsyncMock(return_value='{"result": {"value": {}}}')
        mock_connect.return_value = mock_ws

        with pytest.raises(Exception, match="Callback error"):
            await monitor_new_tokens(callback=error_callback)


@pytest.mark.asyncio
async def test_monitor_new_tokens_default_callback():
    # Test that when no callback is provided, the default dummy_event_handler is used.
    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        # Set up recv to emit one valid JSON message then cancel.
        mock_ws.recv = AsyncMock(
            side_effect=[
                '{"result": {"value": {"logs": ["default callback"]}}}',
                asyncio.CancelledError,
            ]
        )
        mock_connect.return_value = mock_ws
        task = asyncio.create_task(monitor_new_tokens())
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass


@pytest.mark.asyncio
async def test_subscribe_to_events_account_subscription():
    mock_callback = AsyncMock()

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        # Set up recv to return subscription confirmation then cancel
        mock_ws.recv = AsyncMock(
            side_effect=[
                '{"result": "subscription_id"}',  # First response is subscription ID
                asyncio.CancelledError,  # Break the loop
            ]
        )
        mock_connect.return_value = mock_ws

        task = asyncio.create_task(
            subscribe_to_events(
                program_id="test_program",
                callback=mock_callback,
                subscription_type="account",  # This should hit line 48
            )
        )

        # Wait a short time for the subscription to be sent
        await asyncio.sleep(0.1)

        # Cancel and cleanup
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

        # Verify the correct request was sent
        mock_ws.send.assert_called_once()
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["method"] == "accountSubscribe"
        assert sent_data["params"][0] == "test_program"


def test_load_pump_idl():
    idl = load_pump_idl()
    # Verify that the returned IDL is a dict with the expected keys.
    assert isinstance(idl, dict)
    assert "version" in idl
    assert "name" in idl
    assert "instructions" in idl
