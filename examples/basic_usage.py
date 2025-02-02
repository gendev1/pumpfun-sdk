import asyncio
import json
from pumpfun_sdk.client import SolanaClient
from pumpfun_sdk.pump_curve import BondingCurveState
from pumpfun_sdk.utils import (
    load_idl,
    subscribe_to_events,
    process_bonding_curve_state,
    monitor_new_tokens
)

async def example_check_token_status(mint_address: str):
    """Check the status of a token's bonding curve."""
    try:
        # Get and analyze the bonding curve state
        analysis = await process_bonding_curve_state(mint_address)
        
        print("\nToken Status:")
        print("-" * 50)
        print(f"Token Mint: {mint_address}")
        for key, value in analysis.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"Error checking token status: {e}")

async def example_monitor_new_tokens():
    """Monitor for new token creations with custom callback."""
    async def token_handler(event_data):
        if 'result' in event_data and 'value' in event_data['result']:
            logs = event_data['result']['value'].get('logs', [])
            if any("Program log: Instruction: Create" in log for log in logs):
                print("\nNew Token Creation Detected!")
                print("-" * 50)
                for log in logs:
                    print(log)

    print("Starting token monitoring...")
    await monitor_new_tokens(callback=token_handler)

async def main():
    try:
        # Example 1: Check token status
        print("\nExample 1: Checking token status")
        await example_check_token_status("YourTokenMintAddress")
        
        # Example 2: Monitor new tokens
        print("\nExample 2: Monitoring new tokens")
        await example_monitor_new_tokens()
        
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 