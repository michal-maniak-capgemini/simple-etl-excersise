from abc import ABC, abstractmethod
from typing import Any, List

from backend.common.models.cart_dto import CartDto
from backend.common.models.product_from_cart_dto import ProductFromCartDto


class ProductFromCartServiceInterface(ABC):
    @abstractmethod
    def process_products_from_carts(self, cart: Any, cart_dto: CartDto) -> None:
        pass

    @abstractmethod
    def get_bought_products_from_carts(self) -> List[ProductFromCartDto]:
        pass
