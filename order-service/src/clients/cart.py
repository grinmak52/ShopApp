import httpx

from database.core.config import settings
from service.exceptions import ServiceUnavailableError


class CartClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.cart.url, timeout=settings.cart.timeout
        )

    @staticmethod
    def _headers(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    async def get_items(self, token: str) -> list[dict]:
        try:
            resp = await self.client.get("/api/v1/cart", headers=self._headers(token))
        except httpx.HTTPError:
            raise ServiceUnavailableError("Cart is unavailable")
        if resp.status_code != 200:
            raise ServiceUnavailableError("Cart returned an error")
        return resp.json()["items"]

    async def clear(self, token: str) -> None:
        resp = await self.client.delete("/api/v1/cart", headers=self._headers(token))
        resp.raise_for_status()

    async def close(self) -> None:
        await self.client.aclose()


cart_client = CartClient()