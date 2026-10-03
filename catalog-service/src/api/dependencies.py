from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cache.redis import cache
from database.orm.db_helper import db_helper
from repositories.category import CategoryRepository
from repositories.product import ProductRepository
from service.category import CategoryService
from service.product import ProductService

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_getter)]


def get_category_service(session: SessionDep) -> CategoryService:
    return CategoryService(CategoryRepository(session), cache)


def get_product_service(session: SessionDep) -> ProductService:
    return ProductService(ProductRepository(session), CategoryRepository(session), cache)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]