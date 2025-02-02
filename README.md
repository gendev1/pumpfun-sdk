# PumpFun SDK

PumpFun SDK is a Python toolkit for interacting with the Pump.fun protocol on the Solana blockchain. This SDK provides modules for building transactions, monitoring on-chain events, decoding transactions with IDL support, and analyzing bonding curve states.

## Table of Contents

-   [Features](#features)
-   [Installation](#installation)
-   [Quick Start](#quick-start)
    -   [Basic Usage](#basic-usage)
    -   [Token Operations](#token-operations)
    -   [User Operations](#user-operations)
    -   [Building Transactions](#building-transactions)
    -   [Monitoring Events](#monitoring-events)
    -   [Transaction Analysis](#transaction-analysis)
-   [Examples](#examples)
-   [Development](#development)
-   [Contributing](#contributing)
-   [License](#license)

## Features

-   **Transaction Building:** Create buy and sell transactions with pre-defined instruction discriminators.
-   **On-Chain Monitoring:** Subscribe to logs and account updates via websockets.
-   **Transaction Analysis:** Decode and analyze transactions using a provided IDL.
-   **Bonding Curve Analysis:** Parse on-chain bonding curve state and compute token prices.
-   **Token Operations:** Retrieve token information, prices, holders, transactions, and liquidity.
-   **User Operations:** Track user's created tokens, trading history, and liquidity positions.

## Installation

Install the SDK using pip:

```bash
pip install pumpfun-sdk
```

## Quick Start

### Basic Usage

This simple example demonstrates how to retrieve the bonding curve state for a token and monitor events for new token creations.

```python
#!/usr/bin/env python
"""
Basic Usage Example for pumpfun_sdk.

This script demonstrates how to:
- Retrieve and analyze the bonding curve state of a token.
- Monitor on-chain events for new token creations.
"""

import asyncio
from pumpfun_sdk.utils import subscribe_to_events, process_bonding_curve_state, monitor_new_tokens

async def example_check_token_status(mint_address: str):
    try:
        analysis = await process_bonding_curve_state(mint_address)
        print("Token Analysis:")
        for key, value in analysis.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error checking token status: {e}")

async def example_monitor_new_tokens():
    async def token_handler(event_data):
        if 'result' in event_data and 'value' in event_data['result']:
            logs = event_data['result']['value'].get('logs', [])
            if logs:
                print("New Token Creation Detected!")
                for log in logs:
                    print(log)
    print("Starting token monitoring...")
    await monitor_new_tokens(callback=token_handler)

async def main():
    await example_check_token_status("YourTokenMintAddress")
    await example_monitor_new_tokens()

if __name__ == "__main__":
    asyncio.run(main())
```

### Token Operations

This example shows how to interact with token-related functionality.

```python
#!/usr/bin/env python
"""
Token Operations Example for pumpfun_sdk.

This script demonstrates how to:
- Get token information and metadata
- Get token price and market cap
- Get token holders
- Get token transactions
- Get token liquidity
"""

import asyncio
from pumpfun_sdk.usecases.token import (
    get_token_info,
    get_token_price,
    get_token_holders,
    get_token_transactions,
    get_token_liquidity
)

async def example_token_operations(mint_address: str):
    # Get comprehensive token information
    token_info = await get_token_info(mint_address)
    print("Token Info:", token_info)

    # Get current token price
    price = await get_token_price(mint_address)
    print("Current Price:", price)

    # Get token holders
    holders = await get_token_holders(mint_address)
    print("Token Holders:", holders)

    # Get recent transactions
    transactions = await get_token_transactions(mint_address, limit=10)
    print("Recent Transactions:", transactions)

    # Get liquidity information
    liquidity = await get_token_liquidity(mint_address)
    print("Liquidity Info:", liquidity)

async def main():
    await example_token_operations("YourTokenMintAddress")

if __name__ == "__main__":
    asyncio.run(main())
```

### User Operations

This example demonstrates how to track user activity and positions.

```python
#!/usr/bin/env python
"""
User Operations Example for pumpfun_sdk.

This script demonstrates how to:
- Get tokens created by a user
- Get tokens bought by a user
- Get tokens sold by a user
- Get user's liquidity positions
- Get user's transaction history
"""

import asyncio
from pumpfun_sdk.usecases.user import (
    get_user_created_tokens,
    get_user_bought_tokens,
    get_user_sold_tokens,
    get_user_liquidity,
    get_user_transactions
)

async def example_user_operations(user_address: str):
    # Get tokens created by the user
    created_tokens = await get_user_created_tokens(user_address)
    print("Created Tokens:", created_tokens)

    # Get tokens bought by the user
    bought_tokens = await get_user_bought_tokens(user_address)
    print("Bought Tokens:", bought_tokens)

    # Get tokens sold by the user
    sold_tokens = await get_user_sold_tokens(user_address)
    print("Sold Tokens:", sold_tokens)

    # Get user's current liquidity positions
    liquidity = await get_user_liquidity(user_address)
    print("Liquidity Positions:", liquidity)

    # Get user's recent transactions
    transactions = await get_user_transactions(user_address, limit=10)
    print("Recent Transactions:", transactions)

async def main():
    await example_user_operations("YourWalletAddress")

if __name__ == "__main__":
    asyncio.run(main())
```

### Building Transactions

This example shows how to build buy and sell transactions.

```python
#!/usr/bin/env python
"""
Trading Example for pumpfun_sdk.

This script demonstrates how to build buy and sell transactions for a Pump token.
"""

import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from pumpfun_sdk.transaction import build_buy_transaction, build_sell_transaction

async def example_transactions():
    # Create a test keypair (replace with your actual keypair)
    payer = Keypair()

    # Example addresses (replace with actual addresses)
    mint = Pubkey.new_unique()
    bonding_curve = Pubkey.new_unique()
    associated_bonding_curve = Pubkey.new_unique()

    # Build a buy transaction (0.1 SOL amount)
    print("=== Building Buy Transaction ===")
    buy_tx = await build_buy_transaction(
        payer=payer,
        mint=mint,
        bonding_curve=bonding_curve,
        associated_bonding_curve=associated_bonding_curve,
        amount=0.1
    )
    print("Buy Transaction:")
    print(buy_tx)

    # Build a sell transaction (100 tokens)
    print("=== Building Sell Transaction ===")
    sell_tx = await build_sell_transaction(
        payer=payer,
        mint=mint,
        bonding_curve=bonding_curve,
        associated_bonding_curve=associated_bonding_curve,
        amount=100
    )
    print("Sell Transaction:")
    print(sell_tx)

async def main():
    await example_transactions()

if __name__ == "__main__":
    asyncio.run(main())
```

### Monitoring Events

This example subscribes to on-chain log events for the Pump program.

```python
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
    async def activity_handler(event_data):
        if 'result' in event_data and 'value' in event_data['result']:
            logs = event_data['result']['value'].get('logs', [])
            if logs:
                print("Program Activity Detected!")
                for log in logs:
                    print(log)
    print(f"Starting monitoring for program: {PUMP_PROGRAM}")
    await subscribe_to_events(
        program_id=str(PUMP_PROGRAM),
        callback=activity_handler,
        subscription_type='logs'
    )

if __name__ == "__main__":
    asyncio.run(monitor_program_activity())
```

### Transaction Analysis

This example demonstrates how to decode a transaction using a provided IDL file. The SDK now uses `load_pump_idl` from `pumpfun_sdk.idl` for loading IDL definitions.

```python
#!/usr/bin/env python
"""
Transaction Analysis Example for pumpfun_sdk.

This script demonstrates how to:
- Load a raw transaction from a file.
- Decode the transaction using a provided IDL.
- Print the decoded instructions.
"""

import asyncio
from pumpfun_sdk.utils import decode_transaction_from_file
from pumpfun_sdk.idl import load_pump_idl

async def analyze_transaction():
    # Replace these with actual file paths
    tx_file = "path/to/transaction.json"
    idl_file = "path/to/idl.json"

    print("=== Analyzing Transaction ===")
    try:
        # This function uses the custom IDL file if provided, otherwise falls back to the built-in Pump Fun IDL.
        await decode_transaction_from_file(tx_file, idl_file)
    except Exception as e:
        print(f"Error analyzing transaction: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_transaction())
```

## Examples

Detailed examples can be found in the `examples/` directory:

-   **basic_usage.py:** Basic utilization including bonding curve analysis and event monitoring.
-   **token_operations.py:** Working with token information and analysis.
-   **user_operations.py:** Tracking user activity and positions.
-   **monitoring_example.py:** Subscribing to on-chain log events.
-   **trading_example.py:** Building buy and sell transactions.
-   **transaction_analysis.py:** Decoding transaction data using IDL support.

## Development

### Setup

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/gendev1/pumpfun-sdk.git
    cd pumpfun-sdk
    ```

2. **Install Dependencies:**

    ```bash
    poetry install
    ```

### Testing

Run the test suite and check coverage:

```bash
poetry run pytest --cov=pumpfun_sdk --cov-report=term-missing
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create your feature branch:
    ```bash
    git checkout -b feature/your-feature
    ```
3. Commit your changes:
    ```bash
    git commit -m 'Add feature'
    ```
4. Push your branch:
    ```bash
    git push origin feature/your-feature
    ```
5. Open a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).
