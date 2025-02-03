import json
import os
from pathlib import Path

# Get the directory containing the IDL files
IDL_DIR = Path(__file__).parent.parent / "idl"


def load_pump_idl() -> dict:
    """Load the Pump Fun IDL."""
    return _load_idl("pump_fun_idl.json")


def load_raydium_idl() -> dict:
    """Load the Raydium AMM IDL."""
    return _load_idl("raydium_amm_idl.json")


def _load_idl(filename: str) -> dict:
    """Helper function to load an IDL file."""
    idl_path = IDL_DIR / filename
    if not idl_path.exists():
        raise FileNotFoundError(f"IDL file not found: {idl_path}")

    with open(idl_path, "r") as f:
        return json.load(f)
