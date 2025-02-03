import asyncio
from solana.rpc.async_api import AsyncClient
from pumpfun_sdk.config import RPC_ENDPOINT


class SolanaClient:
    """A wrapper around the AsyncClient for simplified usage."""

    def __init__(self, endpoint: str = RPC_ENDPOINT):
        self.endpoint = endpoint
        self.client = AsyncClient(endpoint)

    async def get_account_info(self, address: str):
        response = await self.client.get_account_info(address)
        if not response.value or not response.value.data:
            raise ValueError("No data found for account " + address)
        return response.value

    async def close(self):
        await self.client.close()


# Example usage (this logic can be invoked in an example script)
# async def main():
#     client = SolanaClient()
#     info = await client.get_account_info("SomeAccountPublicKey")
#     print(info)
#     await client.close()
#
# if __name__ == "__main__":
#     asyncio.run(main())
