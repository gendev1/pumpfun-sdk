import asyncio
import json
import websockets
from unittest.mock import AsyncMock

from pumpfun_sdk.client import SolanaClient
from pumpfun_sdk.transaction import load_transaction, decode_transaction
from pumpfun_sdk.pump_curve import BondingCurveState, calculate_bonding_curve_price
from pumpfun_sdk.analytics import analyze_curve_state, print_analysis
from pumpfun_sdk.config import PUMP_PROGRAM, WSS_ENDPOINT
from pumpfun_sdk.idl import load_pump_idl, load_raydium_idl

async def subscribe_to_events(program_id: str, callback, endpoint: str = None, subscription_type: str = 'account'):
    """Subscribe to on-chain events for a given program."""
    # Validate subscription type first
    if subscription_type not in ['account', 'logs']:
        raise ValueError("Unknown subscription type")

    endpoint = endpoint or WSS_ENDPOINT
    
    # Create connection
    ws = await websockets.connect(endpoint)
    try:
        if subscription_type == 'logs':
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "logsSubscribe",
                "params": [ {"mentions": [program_id]}, {"commitment": "confirmed"} ]
            }
        elif subscription_type == 'account':
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "accountSubscribe",
                "params": [ program_id, {"commitment": "confirmed"} ]
            }
            
        await ws.send(json.dumps(request))
        while True:
            msg = await ws.recv()
            await callback(json.loads(msg))
    finally:
        await ws.close()

async def dummy_event_handler(event_data):
    """
    A sample callback to be used with event subscriptions.
    
    :param event_data: Event data received from the subscription.
    """
    print("Received event:")
    print(json.dumps(event_data, indent=2))

async def example_subscribe_to_logs(program_id: str):
    """
    An example function to subscribe to logs for a given program.
    
    It uses dummy_event_handler above and demonstrates a continuous subscription.
    
    :param program_id: Program ID to filter logs for.
    """
    print("Starting logs subscription...")
    await subscribe_to_events(program_id, dummy_event_handler, subscription_type='logs')

async def process_bonding_curve_state(bonding_curve_account: str):
    """Process bonding curve state and run analytics."""
    client = SolanaClient()
    try:
        account_info = await client.get_account_info(bonding_curve_account)
        data = account_info.data
        try:
            state = BondingCurveState(data)
            analysis = analyze_curve_state(data)
            print_analysis(analysis)
            return analysis
        except ValueError as e:
            # Wrap the error with more context
            raise ValueError(f"Invalid bonding curve data: {str(e)}")
    finally:
        await client.close()

async def decode_transaction_from_file(file_path: str, idl_file: str = None):
    """
    Load a raw transaction from file, decode it using the provided IDL, and print the instructions.
    
    :param file_path: Path to the JSON file containing raw transaction data.
    :param idl_file: Optional path to a custom IDL JSON file. If not provided, uses the built-in Pump Fun IDL.
    """
    if idl_file:
        with open(idl_file, 'r') as f:
            idl = json.load(f)
    else:
        idl = load_pump_idl()
    
    tx_data = load_transaction(file_path)
    instructions = decode_transaction(tx_data, idl)
    print("Decoded Transaction Instructions:")
    for ix in instructions:
        print(json.dumps(ix, indent=2))

async def process_block_data(block_data: dict, callback):
    """Process incoming block data and call the callback with relevant events."""
    if 'result' in block_data and 'value' in block_data['result']:
        await callback(block_data['result']['value'])

async def monitor_new_tokens(callback=None):
    """Monitor for new token creations."""
    if callback is None:
        callback = dummy_event_handler
        
    ws = await websockets.connect(WSS_ENDPOINT)
    try:
        subscription_message = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "blockSubscribe",
            "params": [
                {"mentionsAccountOrProgram": str(PUMP_PROGRAM)},
                {
                    "commitment": "confirmed",
                    "encoding": "base64",
                    "transactionDetails": "full"
                }
            ]
        })
        
        await ws.send(subscription_message)
        while True:
            msg = await ws.recv()
            await process_block_data(json.loads(msg), callback)
    finally:
        await ws.close()



