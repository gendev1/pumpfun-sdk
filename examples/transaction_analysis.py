import asyncio
from pumpfun_sdk import (
    SolanaClient,
    PUMP_PROGRAM
)
from pumpfun_sdk.utils import (
    load_idl,
    decode_transaction_from_file
)
from pumpfun_sdk.transaction import (
    load_transaction,
    decode_transaction,
    get_instruction_name,
    get_instruction_discriminator
)

async def analyze_transaction_with_idl(tx_file: str, idl_file: str):
    """
    Analyze a transaction using the provided IDL
    """
    print(f"\nAnalyzing transaction from {tx_file}")
    print("-" * 50)
    
    # Load and decode the transaction
    idl = load_idl(idl_file)
    tx_data = load_transaction(tx_file)
    instructions = decode_transaction(tx_data, idl)
    
    # Print analysis
    print("Transaction Analysis:")
    for idx, ix in enumerate(instructions):
        print(f"\nInstruction {idx + 1}:")
        print(f"Program: {ix['programId']}")
        print(f"Instruction Name: {ix['instruction_name']}")
        
        # Get the discriminator for this instruction
        if ix['instruction_name'] != "unknown":
            discriminator = get_instruction_discriminator(ix['instruction_name'])
            print(f"Discriminator: {discriminator.hex()}")
        
        print(f"Number of Accounts: {len(ix['accounts'])}")
        print("\nAccounts involved:")
        for acc in ix['accounts']:
            print(f"  - {acc}")
        
        print("\nInstruction Data:")
        print(f"  {ix['data']}")

async def analyze_multiple_transactions(tx_files: list, idl_file: str):
    """
    Analyze multiple transactions and provide a summary
    """
    instruction_counts = {}
    program_counts = {}
    
    for tx_file in tx_files:
        tx_data = load_transaction(tx_file)
        idl = load_idl(idl_file)
        instructions = decode_transaction(tx_data, idl)
        
        for ix in instructions:
            # Count instruction types
            inst_name = ix['instruction_name']
            instruction_counts[inst_name] = instruction_counts.get(inst_name, 0) + 1
            
            # Count program invocations
            program_id = ix['programId']
            program_counts[program_id] = program_counts.get(program_id, 0) + 1
    
    print("\nTransaction Analysis Summary")
    print("-" * 50)
    print("\nInstruction Type Distribution:")
    for inst, count in instruction_counts.items():
        print(f"{inst}: {count}")
        if inst != "unknown":
            discriminator = get_instruction_discriminator(inst)
            print(f"  Discriminator: {discriminator.hex()}")
    
    print("\nProgram Invocation Distribution:")
    for prog, count in program_counts.items():
        print(f"{prog}: {count}")

async def analyze_transactions():
    """Analyze transaction(s) using the updated SDK functions."""
    # Replace with your actual file paths
    idl_path = "path/to/your/idl.json"
    tx_path = "path/to/your/transaction.json"
    
    print("\n=== Analyzing Transaction ===")
    try:
        await decode_transaction_from_file(tx_path, idl_path)
    except Exception as e:
        print(f"Error analyzing transaction: {e}")

async def main():
    try:
        await analyze_transactions()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 