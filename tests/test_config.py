import pytest
from pumpfun_sdk.config import (
    set_endpoints,
    get_endpoints,
    DEFAULT_RPC_ENDPOINT,
    DEFAULT_WSS_ENDPOINT,
)


def test_set_endpoints():
    custom_rpc = "https://custom-rpc.com"
    custom_wss = "wss://custom-wss.com"

    set_endpoints(custom_rpc, custom_wss)
    rpc, wss = get_endpoints()

    assert rpc == custom_rpc
    assert wss == custom_wss


def test_set_endpoints_partial():
    original_rpc, original_wss = get_endpoints()
    custom_rpc = "https://custom-rpc.com"

    set_endpoints(rpc_endpoint=custom_rpc)
    rpc, wss = get_endpoints()

    assert rpc == custom_rpc
    assert wss == original_wss


def test_reset_endpoints():
    set_endpoints(DEFAULT_RPC_ENDPOINT, DEFAULT_WSS_ENDPOINT)
    rpc, wss = get_endpoints()

    assert rpc == DEFAULT_RPC_ENDPOINT
    assert wss == DEFAULT_WSS_ENDPOINT
