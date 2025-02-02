import pytest
import json
import tempfile
import os
from pumpfun_sdk.analytics import analyze_curve_state, print_analysis, write_analysis_to_json
from pumpfun_sdk.config import EXPECTED_DISCRIMINATOR

@pytest.fixture
def mock_curve_data():
    # Create valid test data with correct discriminator
    data = bytearray(EXPECTED_DISCRIMINATOR)  # Use correct discriminator
    data.extend((1000).to_bytes(8, 'little'))  # virtual_token_reserves
    data.extend((2000).to_bytes(8, 'little'))  # virtual_sol_reserves
    data.extend((500).to_bytes(8, 'little'))   # real_token_reserves
    data.extend((1000).to_bytes(8, 'little'))  # real_sol_reserves
    data.extend((1500).to_bytes(8, 'little'))  # token_total_supply
    data.extend((1).to_bytes(1, 'little'))     # complete flag
    return bytes(data)

def test_analyze_curve_state(mock_curve_data):
    analysis = analyze_curve_state(mock_curve_data)
    assert isinstance(analysis, dict)
    assert 'price_sol' in analysis
    assert 'virtual_token_reserves' in analysis
    assert analysis['virtual_token_reserves'] == 1000
    assert analysis['virtual_sol_reserves'] == 2000

def test_print_analysis(capsys, mock_curve_data):
    analysis = analyze_curve_state(mock_curve_data)
    print_analysis(analysis)
    captured = capsys.readouterr()
    assert "Bonding Curve Analysis:" in captured.out
    assert "price_sol" in captured.out

def test_write_analysis_to_json(mock_curve_data):
    analysis = analyze_curve_state(mock_curve_data)
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        write_analysis_to_json(analysis, tmp_file.name)
        
        # Verify the file was written correctly
        with open(tmp_file.name, 'r') as f:
            loaded_analysis = json.load(f)
            assert loaded_analysis == analysis
    
    # Cleanup
    os.unlink(tmp_file.name) 