import httpx

from core.config import settings
from service.exceptions import (
    BadRequestError,
    NotFoundError,
    ServiceUnavailableError,
)


class CatalogClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.catalog.url, timeout=settings.catalog.timeout
        )

    async def ensure_available(self, product_id) -> None:
        try:
            resp = await self.client.get(f"/api/v1/products/{product_id}")
        except httpx.HTTPError:
            raise ServiceUnavailableError("Catalog is unavailable")

        if resp.status_code == 404:
            raise NotFoundError("Product")
        if resp.status_code != 200:
            raise ServiceUnavailableError("Catalog returned an error")
        if not resp.json().get("is_active"):
            raise BadRequestError("Product is not available")

    async def close(self) -> None:
        await self.client.aclose()


catalog_client = CatalogClient()