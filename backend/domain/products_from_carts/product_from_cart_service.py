from typing import List

from sqlalchemy.orm import Session

from backend.common.models.cart_dto import CartDto
from backend.common.models.product_from_cart_dto import ProductFromCartDto
from backend.common.utils.file_util import FileUtil
from backend.common.utils.logger import logger
from backend.database.entities.product_from_cart import ProductFromCart
from backend.interfaces.product_from_cart_service_interface import (
    ProductFromCartServiceInterface,
)


class ProductFromCartService(ProductFromCartServiceInterface):
    def __init__(self, db_session: Session):
        self.__db_session = db_session

    def process_products_from_carts(self, cart, cart_dto: CartDto) -> None:
        products = cart.get("products")
        if products:
            logger.info(f"Processing products for cart ID: {cart_dto.cart_id}")
            for product in products:
                product_id = product.get("id")
                logger.info(f"Processing product from cart with ID: {product_id}")
                product_dto = ProductFromCartDto(
                    cart_id=cart_dto.cart_id,
                    product_id=product_id,
                    quantity=product.get("quantity"),
                )
                self.__add_product_to_db(product_dto)
                self.__add_product_to_txt(product_dto)

    def get_bought_products_from_carts(self) -> List[ProductFromCartDto]:
        with self.__db_session:
            logger.info("Fetching all products from carts from DB")
            bought_products_from_carts_entities = self.__db_session.query(
                ProductFromCart
            ).all()
            return [
                ProductFromCartDto.model_validate(product)
                for product in bought_products_from_carts_entities
            ]

    def __add_product_to_db(self, product_from_cart_dto: ProductFromCartDto) -> None:
        product_from_cart_entity = ProductFromCart(
            cart_id=product_from_cart_dto.cart_id,
            product_id=product_from_cart_dto.product_id,
            quantity=product_from_cart_dto.quantity,
        )

        with self.__db_session:
            logger.info(f"Adding product from cart to DB: {product_from_cart_entity}")
            self.__db_session.add(product_from_cart_entity)
            self.__db_session.commit()

    def __add_product_to_txt(self, product_from_cart_dto: ProductFromCartDto) -> None:
        logger.info(
            f"Adding product from cart to the txt file: {product_from_cart_dto}"
        )
        FileUtil.save_result_to_txt_file(
            "products_from_carts.txt", product_from_cart_dto
        )
