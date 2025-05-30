from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List


class DummyJSONApiInterface(ABC):
    @abstractmethod
    def get_users(self) -> Generator[List[Dict[str, Any]], None, None]:
        pass

    @abstractmethod
    def get_carts(self) -> Generator[List[Dict[str, Any]], None, None]:
        pass

    @abstractmethod
    def get_products(self) -> Generator[List[Dict[str, Any]], None, None]:
        pass
