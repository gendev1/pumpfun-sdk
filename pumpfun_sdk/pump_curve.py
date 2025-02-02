import struct
from construct import Struct, Int64ul, Flag
from pumpfun_sdk.config import LAMPORTS_PER_SOL, TOKEN_DECIMALS, EXPECTED_DISCRIMINATOR

# Define a basic construct for the bonding curve state data structure.
BondingCurveStateStruct = Struct(
    "virtual_token_reserves" / Int64ul,
    "virtual_sol_reserves" / Int64ul,
    "real_token_reserves" / Int64ul,
    "real_sol_reserves" / Int64ul,
    "token_total_supply"  / Int64ul,
    "complete"            / Flag
)

class BondingCurveState:
    """Represents the bonding curve state fetched from on-chain data."""
    def __init__(self, data: bytes):
        """Initialize bonding curve state from binary data."""
        # Validate discriminator
        if data[:8] != EXPECTED_DISCRIMINATOR:
            raise ValueError("Invalid discriminator")
            
        # Skip the first 8 bytes (discriminator) then parse the state.
        parsed = BondingCurveStateStruct.parse(data[8:])
        self.virtual_token_reserves = parsed.virtual_token_reserves
        self.virtual_sol_reserves = parsed.virtual_sol_reserves
        self.real_token_reserves = parsed.real_token_reserves
        self.real_sol_reserves = parsed.real_sol_reserves
        self.token_total_supply = parsed.token_total_supply
        self.complete = parsed.complete

    def __repr__(self):
        return (f"BondingCurveState(virtualToken={self.virtual_token_reserves}, "
                f"virtualSOL={self.virtual_sol_reserves}, realToken={self.real_token_reserves}, "
                f"realSOL={self.real_sol_reserves}, totalSupply={self.token_total_supply}, "
                f"complete={self.complete})")

def calculate_bonding_curve_price(curve_state: BondingCurveState) -> float:
    """
    Calculate the token price in SOL based on the bonding curve.
    """
    # Check if reserves are valid
    if curve_state.virtual_token_reserves <= 0 or curve_state.virtual_sol_reserves <= 0:
        raise ValueError("Invalid bonding curve reserves")
    
    token_price = (curve_state.virtual_sol_reserves / LAMPORTS_PER_SOL) / (curve_state.virtual_token_reserves / 10 ** TOKEN_DECIMALS)
    return token_price 

def calculate_output_amount(
    curve_state: BondingCurveState,
    input_amount: float,
    is_buy: bool = True
) -> float:
    """
    Calculate expected output amount for a given input amount.
    
    :param curve_state: Current bonding curve state
    :param input_amount: Input amount (in SOL for buys, tokens for sells)
    :param is_buy: True for buy calculations, False for sell
    :return: Expected output amount
    """
    if is_buy:
        virtual_sol = curve_state.virtual_sol_reserves + int(input_amount * LAMPORTS_PER_SOL)
        virtual_tokens = curve_state.virtual_token_reserves
    else:
        virtual_sol = curve_state.virtual_sol_reserves
        virtual_tokens = curve_state.virtual_token_reserves + int(input_amount * 10**TOKEN_DECIMALS)
    
    return (virtual_sol / LAMPORTS_PER_SOL) / (virtual_tokens / 10**TOKEN_DECIMALS) 