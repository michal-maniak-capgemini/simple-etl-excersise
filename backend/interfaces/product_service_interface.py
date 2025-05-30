from abc import ABC, abstractmethod


class ProductServiceInterface(ABC):
    @abstractmethod
    def process_products(self) -> None:
        pass

    @abstractmethod
    def get_all_products(self):
        pass
