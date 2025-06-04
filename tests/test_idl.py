import pytest
from pumpfun_sdk.idl import load_pump_idl, load_raydium_idl, _load_idl


def test_load_pump_idl():
    idl = load_pump_idl()
    assert isinstance(idl, dict)
    assert "version" in idl
    assert "name" in idl


def test_load_raydium_idl():
    idl = load_raydium_idl()
    assert isinstance(idl, dict)
    assert "version" in idl
    assert "name" in idl


def test_load_idl_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        _load_idl("non_existent.json")
