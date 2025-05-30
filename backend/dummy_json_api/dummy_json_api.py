from typing import Any, Dict, Generator, List

import requests
from requests import Response

from backend.common.utils.logger import logger
from backend.interfaces.dummy_json_api_interface import DummyJSONApiInterface


class DummyJSONApi(DummyJSONApiInterface):
    __USERS: str = "users"
    __CARTS: str = "carts"
    __PRODUCTS: str = "products"
    __USERS_URL: str = f"https://dummyjson.com/{__USERS}"
    __CARTS_URL: str = f"https://dummyjson.com/{__CARTS}"
    __PRODUCTS_URL: str = f"https://dummyjson.com/{__PRODUCTS}"
    __batch_size: int = 10

    def get_users(self) -> Generator[List[Dict[str, Any]], None, None]:
        return self.__fetch_data(self.__USERS_URL, self.__USERS)

    def get_carts(self) -> Generator[List[Dict[str, Any]], None, None]:
        return self.__fetch_data(self.__CARTS_URL, self.__CARTS)

    def get_products(self) -> Generator[List[Dict[str, Any]], None, None]:
        return self.__fetch_data(self.__PRODUCTS_URL, self.__PRODUCTS)

    def __fetch_data(
        self, url: str, data_name: str
    ) -> Generator[List[Dict[str, Any]], None, None]:
        skip: int = 0
        logger.info(f"Fetching {data_name} from DummyJSON API")
        while True:
            params: Dict[str, int] = {"limit": self.__batch_size, "skip": skip}
            response: Response = requests.get(url, verify=False, params=params)
            response.raise_for_status()
            data_batch: dict = response.json()

            if not data_batch.get(data_name):
                logger.info(f"No more {data_name} to process.")
                break

            yield data_batch.get(data_name)
            logger.info(f"Taking next batch with params: {params}!!!")
            skip += self.__batch_size
