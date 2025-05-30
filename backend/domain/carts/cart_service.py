from typing import Any, Dict, List

from sqlalchemy.orm import Session

from backend.common.models.cart_dto import CartDto
from backend.common.utils.file_util import FileUtil
from backend.common.utils.logger import logger
from backend.database.entities.cart import Cart
from backend.interfaces.cart_service_interface import CartServiceInterface
from backend.interfaces.product_from_cart_service_interface import (
    ProductFromCartServiceInterface,
)
from backend.interfaces.dummy_json_api_interface import DummyJSONApiInterface


class CartService(CartServiceInterface):
    __CARTS_TXT: str = "carts.txt"
    __PRODUCTS_FROM_CARTS_TXT: str = "products_from_carts.txt"

    def __init__(
        self,
        dummy_json_api: DummyJSONApiInterface,
        db_session: Session,
        product_from_cart_service: ProductFromCartServiceInterface,
    ):
        self.__dummy_json_api: DummyJSONApiInterface = dummy_json_api
        self.__db_session: Session = db_session
        self.__product_from_cart_service: ProductFromCartServiceInterface = (
            product_from_cart_service
        )

    def get_all_carts(self):
        with self.__db_session:
            logger.info("Fetching all carts from DB")
            carts_entities = self.__db_session.query(Cart).all()
            return [CartDto.model_validate(cart) for cart in carts_entities]

    def process_carts(self) -> None:
        FileUtil.clean_txt_file_before_processing(self.__CARTS_TXT)
        FileUtil.clean_txt_file_before_processing(self.__PRODUCTS_FROM_CARTS_TXT)
        for carts_batch in self.__dummy_json_api.get_carts():
            self.__process_single_batch_of_carts(carts_batch)

    def __process_single_batch_of_carts(self, carts: List[Dict[str, Any]]) -> None:
        for cart in carts:
            cart_id: int = cart.get("id")
            logger.info(f"Processing cart with ID: {cart_id}")
            is_cart_in_db: bool = self.__is_cart_in_db(cart_id)
            if not is_cart_in_db:
                cart_dto: CartDto = CartDto(
                    cart_id=cart_id,
                    user_id=cart.get("userId"),
                )
                self.__add_cart_to_db(cart_dto)
                self.__add_cart_to_txt(cart_dto)

                self.__product_from_cart_service.process_products_from_carts(
                    cart, cart_dto
                )
            else:
                logger.info(
                    f"Cart with ID: {cart_id} already exists in DB, skipping..."
                )

    def __is_cart_in_db(self, cart_id: int) -> bool:
        with self.__db_session:
            logger.info(f"Checking if cart with ID: {cart_id} exists in DB")
            count: int = (
                self.__db_session.query(Cart).filter(Cart.cart_id == cart_id).count()
            )
            return count > 0

    def __add_cart_to_db(self, cart_dto: CartDto) -> None:
        cart_entity = Cart(
            cart_id=cart_dto.cart_id,
            user_id=cart_dto.user_id,
        )

        with self.__db_session:
            logger.info(f"Adding cart to DB: {cart_entity}")
            self.__db_session.add(cart_entity)
            self.__db_session.commit()

    def __add_cart_to_txt(self, cart_dto: CartDto) -> None:
        logger.info(f"Adding cart to the txt file: {cart_dto}")
        FileUtil.save_result_to_txt_file(self.__CARTS_TXT, cart_dto)
