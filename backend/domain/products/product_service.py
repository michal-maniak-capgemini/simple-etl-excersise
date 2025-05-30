from typing import List

from sqlalchemy.orm import Session

from backend.common.models.product_dto import ProductDto
from backend.common.utils.file_util import FileUtil
from backend.common.utils.logger import logger
from backend.database.entities.product import Product
from backend.interfaces.product_service_interface import ProductServiceInterface
from backend.interfaces.dummy_json_api_interface import DummyJSONApiInterface


class ProductService(ProductServiceInterface):
    __PRODUCT_TXT: str = "products.txt"

    def __init__(self, dummy_json_api: DummyJSONApiInterface, db_session: Session):
        self.__dummy_json_api: DummyJSONApiInterface = dummy_json_api
        self.__db_session: Session = db_session

    def get_all_products(self) -> List[ProductDto]:
        with self.__db_session:
            logger.info("Fetching all products from DB")
            products_entities = self.__db_session.query(Product).all()
            return [ProductDto.model_validate(product) for product in products_entities]

    def process_products(self) -> None:
        FileUtil.clean_txt_file_before_processing(self.__PRODUCT_TXT)
        for products_batch in self.__dummy_json_api.get_products():
            self.__process_single_batch_of_products(products_batch)

    def __process_single_batch_of_products(self, products: list) -> None:
        for product in products:
            product_id: int = product.get("id")
            logger.info(f"Processing product with ID: {product_id}")
            is_product_in_db: bool = self.__is_product_in_db(product_id)
            if not is_product_in_db:
                product_dto: ProductDto = ProductDto(
                    title=product.get("title"),
                    price=product.get("price"),
                    category=product.get("category"),
                    description=product.get("description"),
                    product_id=product_id,
                )
                self.__add_product_to_db(product_dto)
                self.__add_product_to_txt(product_dto)
            else:
                logger.info(
                    f"Product with ID: {product_id} already exists in DB, skipping..."
                )

    def __is_product_in_db(self, product_id: int) -> bool:
        with self.__db_session:
            logger.info(f"Checking if product with ID: {product_id} exists in DB")
            count: int = (
                self.__db_session.query(Product)
                .filter(Product.product_id == product_id)
                .count()
            )

            return count > 0

    def __add_product_to_db(self, product_dto: ProductDto) -> None:
        product_entity = Product(
            title=product_dto.title,
            price=product_dto.price,
            category=product_dto.category,
            description=product_dto.description,
            product_id=product_dto.product_id,
        )

        with self.__db_session:
            logger.info(f"Adding product to DB: {product_entity}")
            self.__db_session.add(product_entity)
            self.__db_session.commit()

    def __add_product_to_txt(self, product_dto: ProductDto) -> None:
        logger.info(f"Adding product to the txt file: {product_dto}")
        FileUtil.save_result_to_txt_file(self.__PRODUCT_TXT, product_dto)
