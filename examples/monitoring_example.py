#!/usr/bin/env python
"""
Monitoring Example for pumpfun_sdk.

This script demonstrates how to subscribe to on-chain log events using
the subscribe_to_events function.
"""

import asyncio
from pumpfun_sdk import PUMP_PROGRAM
from pumpfun_sdk.utils import subscribe_to_events

async def monitor_program_activity():
    """Monitor all activity for the Pump program."""
    async def activity_handler(event_data):
        if 'result' in event_data and 'value' in event_data['result']:
            logs = event_data['result']['value'].get('logs', [])
            if logs:
                print("\nProgram Activity Detected!")
                print("-" * 50)
                for log in logs:
                    print(log)

    print(f"Starting monitoring for program: {PUMP_PROGRAM}")
    await subscribe_to_events(
        program_id=str(PUMP_PROGRAM),
        callback=activity_handler,
        subscription_type='logs'
    )

async def monitor_liquidity_migrations():
    """
    Monitor specifically for liquidity migration events
    """
    async def migration_handler(event_data):
        if 'result' in event_data and 'value' in event_data['result']:
            logs = event_data['result']['value'].get('logs', [])
            if any("Instruction: Migrate" in log for log in logs):
                print("\nLiquidity Migration Detected!")
                print("-" * 50)
                for log in logs:
                    print(log)
                print("-" * 50)

    print(f"Starting monitoring for liquidity migrations")
    await subscribe_to_events(
        program_id=PUMP_PROGRAM,
        callback=migration_handler,
        subscription_type='logs'
    )

async def main():
    try:
        await monitor_program_activity()
        
        # Monitor liquidity migrations
        # await monitor_liquidity_migrations()
        
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 