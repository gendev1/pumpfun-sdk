# PumpFun SDK

A Python SDK for interacting with the Pump.fun protocol on Solana. This SDK simplifies token trading, on-chain event monitoring, transaction analysis, and bonding curve state processing.

## Table of Contents

-   [Features](#features)
-   [Installation](#installation)
-   [Quick Start](#quick-start)
    -   [Basic Usage](#basic-usage)
    -   [Building Transactions](#building-transactions)
    -   [Monitoring Events](#monitoring-events)
    -   [Transaction Analysis](#transaction-analysis)
-   [Examples](#examples)
-   [Development](#development)
-   [Contributing](#contributing)
-   [License](#license)

## Features

-   **Transaction Building:** Create buy and sell transactions for Pump tokens.
-   **On-Chain Monitoring:** Subscribe to program events and monitor new token creations.
-   **Transaction Analysis:** Decode and analyze transactions using provided IDLs.
-   **Bonding Curve Analysis:** Calculate prices and analyze bonding curve states.

## Installation

Install the SDK via pip:

```bash
pip install pumpfun-sdk
```

## Quick Start

### Basic Usage

Below is a simple example that retrieves and prints the bonding curve state for a given token mint.

```python
import asyncio
from pumpfun_sdk.utils import process_bonding_curve_state

async def check_token_status(mint_address: str):
    try:
        # Get and analyze the bonding curve state
        analysis = await process_bonding_curve_state(mint_address)
        print("Token Analysis:")
        for key, value in analysis.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error: {e}")

# Run the example
asyncio.run(check_token_status("YourTokenMintAddress"))
```

### Building Transactions

The SDK allows you to build transactions for buying or selling tokens. Replace the placeholder addresses with actual ones.

```python
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from pumpfun_sdk.transaction import build_buy_transaction, build_sell_transaction

async def example_transactions():
    # Create test keypair (replace with your actual keypair)
    payer = Keypair()

    # Example addresses (replace with actual addresses)
    mint = Pubkey.new_unique()
    bonding_curve = Pubkey.new_unique()
    associated_bonding_curve = Pubkey.new_unique()

    # Build buy transaction (0.1 SOL amount)
    buy_tx = await build_buy_transaction(
        payer=payer,
        mint=mint,
        bonding_curve=bonding_curve,
        associated_bonding_curve=associated_bonding_curve,
        amount=0.1
    )
    print("Buy Transaction built:")
    print(buy_tx)

    # Build sell transaction (100 token amount)
    sell_tx = await build_sell_transaction(
        payer=payer,
        mint=mint,
        bonding_curve=bonding_curve,
        associated_bonding_curve=associated_bonding_curve,
        amount=100
    )
    print("Sell Transaction built:")
    print(sell_tx)

# To run the example:
# asyncio.run(example_transactions())
```

### Monitoring Events

Subscribe to on-chain events to monitor your program activity.

```python
from pumpfun_sdk.utils import subscribe_to_events

async def monitor_program_activity(program_id: str):
    async def activity_handler(event_data):
        if 'result' in event_data and 'value' in event_data['result']:
            logs = event_data['result']['value'].get('logs', [])
            if logs:
                print("Program Activity Detected!")
                for log in logs:
                    print(log)

    await subscribe_to_events(
        program_id=program_id,
        callback=activity_handler,
        subscription_type='logs'
    )

# Usage:
# asyncio.run(monitor_program_activity("YourProgramID"))
```

### Transaction Analysis

Decode transactions using an IDL file.

```python
from pumpfun_sdk.utils import decode_transaction_from_file

async def analyze_transaction():
    await decode_transaction_from_file(
        tx_file="path/to/transaction.json",
        idl_file="path/to/idl.json"
    )

# Usage:
# asyncio.run(analyze_transaction())
```

## Examples

Check the `examples/` directory for more detailed examples:

-   **basic_usage.py:** Basic SDK usage examples.
-   **monitoring_example.py:** Program activity monitoring.
-   **trading_example.py:** Building buy/sell transactions.
-   **transaction_analysis.py:** Transaction decoding and analysis.

## Development

### Setup

1. Clone the repository:

```bash
git clone https://github.com/gendev1/pumpfun-sdk.git
cd pumpfun-sdk
```

2. Install dependencies:

```bash
poetry install
```

### Testing

Run the test suite:

```bash
poetry run pytest
```

For test coverage:

```bash
poetry run pytest --cov
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create your feature branch:
    ```bash
    git checkout -b feature/your-feature
    ```
3. Commit your changes:
    ```bash
    git commit -m 'Add some feature'
    ```
4. Push to the branch:
    ```bash
    git push origin feature/your-feature
    ```
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
