from collections import defaultdict
from typing import List, Dict, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.common.models.most_ordered_category_dto import MostOrderedCategoryDto
from backend.common.utils.file_util import FileUtil
from backend.common.utils.logger import logger
from backend.database.entities.cart import Cart
from backend.database.entities.product import Product
from backend.database.entities.product_from_cart import ProductFromCart
from backend.interfaces.category_service_interface import (
    CategoryServiceInterface,
)


class CategoryService(CategoryServiceInterface):
    __CATEGORIES_TXT: str = "most_ordered_categories.txt"

    def __init__(
        self,
        db_session: Session,
    ):
        self.__db_session: Session = db_session

    def get_most_ordered_category(self) -> List[MostOrderedCategoryDto]:
        with self.__db_session:
            logger.info("Fetching most ordered categories from DB")
            results = (
                self.__db_session.query(
                    Cart.user_id,
                    Product.category,
                    func.sum(ProductFromCart.quantity).label("total_orders"),
                )
                .join(
                    ProductFromCart,
                    Cart.cart_id == ProductFromCart.cart_id,
                )
                .join(
                    Product,
                    ProductFromCart.product_id == Product.product_id,
                )
                .group_by(Cart.user_id, Product.category)
                .all()
            )

            # Group by user_id
            user_categories: Dict[int, List[Tuple[str, int]]] = defaultdict(list)
            for user_id, category, total_orders in results:
                user_categories[user_id].append((category, total_orders))

            most_ordered_categories: List[MostOrderedCategoryDto] = []
            for user_id, categories in user_categories.items():
                if not categories:
                    continue
                max_orders: int = max(total for _, total in categories)
                for category, total in categories:
                    if total == max_orders:
                        most_ordered_category: MostOrderedCategoryDto = (
                            MostOrderedCategoryDto(
                                user_id=user_id,
                                category_name=category,
                                total_orders=total,
                            )
                        )
                        most_ordered_categories.append(most_ordered_category)
                        self.__add_most_ordered_categories_to_txt(most_ordered_category)

            return most_ordered_categories

    def __add_most_ordered_categories_to_txt(
        self, most_ordered_category: MostOrderedCategoryDto
    ) -> None:
        logger.info(
            f"Adding most ordered category for one user to the txt file: {most_ordered_category}"
        )
        FileUtil.save_result_to_txt_file(self.__CATEGORIES_TXT, most_ordered_category)
