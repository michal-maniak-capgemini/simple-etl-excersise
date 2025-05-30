from abc import ABC, abstractmethod
from typing import List

from backend.common.models.cart_dto import CartDto


class CartServiceInterface(ABC):
    @abstractmethod
    def process_carts(self) -> None:
        pass

    @abstractmethod
    def get_all_carts(self) -> List[CartDto]:
        pass
