from typing import List

from fastapi import APIRouter, Depends, Request

from backend.common.models.cart_dto import CartDto
from backend.common.models.most_ordered_category_dto import MostOrderedCategoryDto
from backend.common.models.product_dto import ProductDto
from backend.common.models.product_from_cart_dto import ProductFromCartDto
from backend.common.models.user_dto import UserDto
from backend.interfaces.cart_service_interface import CartServiceInterface
from backend.interfaces.category_service_interface import (
    CategoryServiceInterface,
)
from backend.interfaces.product_service_interface import ProductServiceInterface
from backend.interfaces.product_from_cart_service_interface import (
    ProductFromCartServiceInterface,
)
from backend.interfaces.user_service_interface import UserServiceInterface

router = APIRouter()


def get_user_service(request: Request) -> UserServiceInterface:
    return request.app.state.user_service


def get_cart_service(request: Request) -> CartServiceInterface:
    return request.app.state.cart_service


def get_product_service(request: Request) -> ProductServiceInterface:
    return request.app.state.product_service


def get_product_from_cart_service(request: Request) -> ProductFromCartServiceInterface:
    return request.app.state.product_from_cart_service


def get_category_service(request: Request) -> CategoryServiceInterface:
    return request.app.state.category_service


@router.get("/users", response_model=List[UserDto])
async def get_users(user_service: UserServiceInterface = Depends(get_user_service)):
    return user_service.get_all_users()


@router.get("/carts", response_model=List[CartDto])
async def get_carts(cart_service: CartServiceInterface = Depends(get_cart_service)):
    return cart_service.get_all_carts()


@router.get("/products", response_model=List[ProductDto])
async def get_products(
    product_service: ProductServiceInterface = Depends(get_product_service),
):
    return product_service.get_all_products()


@router.get("/products-bought-from-carts", response_model=List[ProductFromCartDto])
async def get_bought_products_from_carts(
    product_from_cart_service: ProductFromCartServiceInterface = Depends(
        get_product_from_cart_service
    ),
):
    return product_from_cart_service.get_bought_products_from_carts()


@router.get("/most-ordered-category", response_model=List[MostOrderedCategoryDto])
async def get_most_ordered_category(
    category_service: CategoryServiceInterface = Depends(get_category_service),
):
    return category_service.get_most_ordered_category()
