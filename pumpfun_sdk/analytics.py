import json
from pumpfun_sdk.client import SolanaClient
from pumpfun_sdk.pump_curve import BondingCurveState, calculate_bonding_curve_price


def analyze_curve_state(data: bytes):
    """
    Given raw bonding curve account data, do some analytics.
    For example, compute the price and print out metrics.
    """
    curve_state = BondingCurveState(data)
    price = calculate_bonding_curve_price(curve_state)
    analysis = {
        "price_sol": price,
        "virtual_token_reserves": curve_state.virtual_token_reserves,
        "virtual_sol_reserves": curve_state.virtual_sol_reserves,
        "real_token_reserves": curve_state.real_token_reserves,
        "real_sol_reserves": curve_state.real_sol_reserves,
        "token_total_supply": curve_state.token_total_supply,
        "complete": curve_state.complete,
    }
    return analysis


def print_analysis(analysis: dict):
    print("Bonding Curve Analysis:")
    print("-" * 50)
    for key, value in analysis.items():
        print(f"{key}: {value}")


def write_analysis_to_json(analysis: dict, file_path: str):
    """
    Write the analysis data to a JSON file.

    :param analysis: Dictionary containing analysis data.
    :param file_path: File path where the JSON data will be saved.
    """
    with open(file_path, "w") as json_file:
        json.dump(analysis, json_file, indent=4)
    print(f"Analysis data written to {file_path}")


# Further analytics functions can be added here. For instance, you could build a module that
# refreshes data periodically, computes moving averages, alerts on events, etc.
