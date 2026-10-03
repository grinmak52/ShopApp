import httpx

from database.core.config import settings
from service.exceptions import BadRequestError, ServiceUnavailableError


class CatalogClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.catalog.url, timeout=settings.catalog.timeout
        )

    async def get_product(self, product_id) -> dict:
        try:
            resp = await self.client.get(f"/api/v1/products/{product_id}")
        except httpx.HTTPError:
            raise ServiceUnavailableError("Catalog is unavailable")
        if resp.status_code == 404:
            raise BadRequestError(f"Product {product_id} no longer exists")
        if resp.status_code != 200:
            raise ServiceUnavailableError("Catalog returned an error")
        return resp.json()

    async def close(self) -> None:
        await self.client.aclose()


catalog_client = CatalogClient()