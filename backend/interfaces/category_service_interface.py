from abc import ABC, abstractmethod
from typing import List

from backend.common.models.most_ordered_category_dto import MostOrderedCategoryDto


class CategoryServiceInterface(ABC):
    @abstractmethod
    def get_most_ordered_category(self) -> List[MostOrderedCategoryDto]:
        pass
