import pytest
from pumpfun_sdk.pump_curve import (
    BondingCurveState,
    calculate_bonding_curve_price,
    calculate_output_amount,
)
from pumpfun_sdk.config import EXPECTED_DISCRIMINATOR


def create_mock_curve_data():
    # Create mock binary data that matches the expected format
    mock_data = bytearray(EXPECTED_DISCRIMINATOR)  # First 8 bytes are discriminator
    # Add mock values for the curve state (8 bytes each for the u64 values)
    mock_data.extend((100).to_bytes(8, "little"))  # virtual_token_reserves
    mock_data.extend((200).to_bytes(8, "little"))  # virtual_sol_reserves
    mock_data.extend((50).to_bytes(8, "little"))  # real_token_reserves
    mock_data.extend((100).to_bytes(8, "little"))  # real_sol_reserves
    mock_data.extend((150).to_bytes(8, "little"))  # token_total_supply
    mock_data.extend((1).to_bytes(1, "little"))  # complete flag
    return bytes(mock_data)


def test_bonding_curve_state_parsing():
    mock_data = create_mock_curve_data()
    state = BondingCurveState(mock_data)

    assert state.virtual_token_reserves == 100
    assert state.virtual_sol_reserves == 200
    assert state.real_token_reserves == 50
    assert state.real_sol_reserves == 100
    assert state.token_total_supply == 150
    assert state.complete == True


def test_calculate_bonding_curve_price():
    mock_data = create_mock_curve_data()
    state = BondingCurveState(mock_data)
    price = calculate_bonding_curve_price(state)

    # Price calculation should be virtual_sol_reserves / virtual_token_reserves
    # Adjusted for decimals
    expected_price = (200 / 1_000_000_000) / (100 / 1_000_000)
    assert price == pytest.approx(expected_price)


def test_invalid_curve_state():
    # Test with zero reserves
    mock_data = bytearray(EXPECTED_DISCRIMINATOR)
    mock_data.extend((0).to_bytes(8, "little") * 5)  # All zeros
    mock_data.extend((0).to_bytes(1, "little"))

    state = BondingCurveState(mock_data)
    with pytest.raises(ValueError, match="Invalid bonding curve reserves"):
        calculate_bonding_curve_price(state)


def test_bonding_curve_zero_reserves():
    # Create curve data with zero reserves
    data = bytearray(EXPECTED_DISCRIMINATOR)
    data.extend((0).to_bytes(8, "little") * 5)  # All zeros
    data.extend((1).to_bytes(1, "little"))

    state = BondingCurveState(data)
    with pytest.raises(ValueError, match="Invalid bonding curve reserves"):
        calculate_bonding_curve_price(state)


def test_bonding_curve_invalid_discriminator():
    data = bytearray(b"invalid!" + b"\x00" * 41)  # Wrong discriminator
    with pytest.raises(ValueError, match="Invalid discriminator"):
        BondingCurveState(data)


def test_calculate_output_amount_buy():
    mock_data = create_mock_curve_data()
    state = BondingCurveState(mock_data)
    output = calculate_output_amount(state, 1.0, is_buy=True)
    assert output > 0


def test_calculate_output_amount_sell():
    mock_data = create_mock_curve_data()
    state = BondingCurveState(mock_data)
    output = calculate_output_amount(state, 100.0, is_buy=False)
    assert output > 0


def test_bonding_curve_state_repr():
    mock_data = create_mock_curve_data()
    state = BondingCurveState(mock_data)
    repr_str = repr(state)
    assert "BondingCurveState" in repr_str
    assert "virtualToken=100" in repr_str
    assert "virtualSOL=200" in repr_str
    assert "complete=True" in repr_str
