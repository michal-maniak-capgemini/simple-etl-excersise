import pytest
from unittest.mock import Mock, patch, MagicMock
import math

from backend.domain.services.product_service import ProductService
from backend.common.models.product_dto import ProductDto
from backend.domain.entities.product import Product
from backend.interfaces.dummy_json_api_interface import DummyJSONApiInterface


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = None
    return session


@pytest.fixture
def mock_dummy_json_api():
    return Mock(spec=DummyJSONApiInterface)


@pytest.fixture
def product_service(mock_db_session, mock_dummy_json_api):
    return ProductService(mock_dummy_json_api, mock_db_session)


class TestGetAllProducts:
    def test_get_all_products_returns_converted_dtos(
        self, product_service, mock_db_session
    ):
        # Arrange
        product1 = Product(
            title="Product 1",
            price=10.5,
            category="Category A",
            description="Desc 1",
            product_id=1,
        )
        product2 = Product(
            title="Product 2",
            price=20.0,
            category="Category B",
            description="Desc 2",
            product_id=2,
        )
        mock_db_session.query.return_value.all.return_value = [product1, product2]

        # Act
        result = product_service.get_all_products()

        # Assert
        mock_db_session.query.assert_called_once_with(Product)
        assert len(result) == 2
        assert all(isinstance(prod, ProductDto) for prod in result)
        assert result[0].title == "Product 1"
        assert math.isclose(result[0].price, 10.5, rel_tol=1e-9)
        assert result[0].category == "Category A"
        assert result[0].description == "Desc 1"
        assert result[0].product_id == 1
        assert result[1].title == "Product 2"
        assert math.isclose(result[1].price, 20.0, rel_tol=1e-9)
        assert result[1].category == "Category B"
        assert result[1].description == "Desc 2"
        assert result[1].product_id == 2

    def test_get_all_products_returns_empty_list_when_no_products(
        self, product_service, mock_db_session
    ):
        # Arrange
        mock_db_session.query.return_value.all.return_value = []

        # Act
        result = product_service.get_all_products()

        # Assert
        mock_db_session.query.assert_called_once_with(Product)
        assert len(result) == 0


class TestProcessProducts:
    @patch("backend.domain.services.product_service.FileUtil")
    def test_process_new_product(
        self, mock_file_util, product_service, mock_dummy_json_api, mock_db_session
    ):
        # Arrange
        product_json = {
            "id": 1,
            "title": "Product 1",
            "price": 10.5,
            "category": "Category A",
            "description": "Desc 1",
        }
        mock_dummy_json_api.get_products.return_value = [[product_json]]
        mock_db_session.query.return_value.filter.return_value.count.return_value = 0

        # Act
        product_service.process_products()

        # Assert
        product_dto = ProductDto(
            title="Product 1",
            price=10.5,
            category="Category A",
            description="Desc 1",
            product_id=1,
        )
        mock_db_session.query.assert_called_with(Product)
        mock_db_session.query.return_value.filter.assert_called_once()
        mock_db_session.query.return_value.filter.return_value.count.assert_called_once()
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_file_util.save_result_to_txt_file.assert_called_once_with(
            "products.txt", product_dto
        )

    @patch("backend.domain.services.product_service.FileUtil")
    def test_process_existing_product(
        self, mock_file_util, product_service, mock_dummy_json_api, mock_db_session
    ):
        # Arrange
        product_json = {
            "id": 1,
            "title": "Product 1",
            "price": 10.5,
            "category": "Category A",
            "description": "Desc 1",
        }
        mock_dummy_json_api.get_products.return_value = [[product_json]]
        mock_db_session.query.return_value.filter.return_value.count.return_value = 1

        # Act
        product_service.process_products()

        # Assert
        mock_db_session.query.assert_called_with(Product)
        mock_db_session.query.return_value.filter.assert_called_once()
        mock_db_session.query.return_value.filter.return_value.count.assert_called_once()
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_file_util.save_result_to_txt_file.assert_not_called()

    @patch("backend.domain.services.product_service.FileUtil")
    def test_process_multiple_product_batches(
        self, mock_file_util, product_service, mock_dummy_json_api, mock_db_session
    ):
        # Arrange
        product1_json = {
            "id": 1,
            "title": "Product 1",
            "price": 10.5,
            "category": "Category A",
            "description": "Desc 1",
        }
        product2_json = {
            "id": 2,
            "title": "Product 2",
            "price": 20.0,
            "category": "Category B",
            "description": "Desc 2",
        }
        batch1 = [product1_json]
        batch2 = [product2_json]
        mock_dummy_json_api.get_products.return_value = [batch1, batch2]
        mock_db_session.query.return_value.filter.return_value.count.side_effect = [
            0,
            0,
        ]

        # Act
        product_service.process_products()

        # Assert
        assert mock_db_session.query.return_value.filter.call_count == 2
        assert mock_db_session.add.call_count == 2
        assert mock_db_session.commit.call_count == 2
        assert mock_file_util.save_result_to_txt_file.call_count == 2

    @patch("backend.domain.services.product_service.FileUtil")
    def test_process_empty_batch(
        self, mock_file_util, product_service, mock_dummy_json_api, mock_db_session
    ):
        # Arrange
        mock_dummy_json_api.get_products.return_value = [[]]

        # Act
        product_service.process_products()

        # Assert
        mock_file_util.clean_txt_file_before_processing.assert_any_call("products.txt")
        mock_dummy_json_api.get_products.assert_called_once()
        mock_db_session.query.assert_not_called()
        mock_db_session.query.return_value.filter.assert_not_called()
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_file_util.save_result_to_txt_file.assert_not_called()
