import pytest
from unittest.mock import Mock, patch, MagicMock

from backend.domain.carts.cart_service import CartService
from backend.common.models.cart_dto import CartDto
from backend.domain.entities.cart import Cart
from backend.interfaces.dummy_json_api_interface import DummyJSONApiInterface
from backend.interfaces.product_from_cart_service_interface import (
    ProductFromCartServiceInterface,
)


@pytest.fixture
def mock_db_session():
    """Fixture for mocking the database session"""
    session = MagicMock()
    # Set up context manager behavior
    session.__enter__.return_value = session
    session.__exit__.return_value = None
    return session


@pytest.fixture
def mock_dummy_json_api():
    """Fixture for mocking the dummy JSON API interface"""
    return Mock(spec=DummyJSONApiInterface)


@pytest.fixture
def mock_product_from_cart_service():
    """Fixture for mocking the product from cart service"""
    return Mock(spec=ProductFromCartServiceInterface)


@pytest.fixture
def cart_service(mock_db_session, mock_dummy_json_api, mock_product_from_cart_service):
    """Fixture for creating a CartService instance with mocked dependencies"""
    return CartService(
        mock_dummy_json_api, mock_db_session, mock_product_from_cart_service
    )


class TestGetAllCarts:
    def test_get_all_carts_returns_converted_dtos(self, cart_service, mock_db_session):
        # Arrange
        cart1 = Cart(cart_id=1, user_id=101)
        cart2 = Cart(cart_id=2, user_id=102)

        mock_db_session.query.return_value.all.return_value = [cart1, cart2]

        # Act
        result = cart_service.get_all_carts()

        # Assert
        mock_db_session.query.assert_called_once_with(Cart)
        assert len(result) == 2
        assert all(isinstance(cart, CartDto) for cart in result)
        assert result[0].cart_id == 1
        assert result[0].user_id == 101
        assert result[1].cart_id == 2
        assert result[1].user_id == 102

    def test_get_all_carts_returns_empty_list_when_no_carts(
        self, cart_service, mock_db_session
    ):
        # Arrange
        mock_db_session.query.return_value.all.return_value = []

        # Act
        result = cart_service.get_all_carts()

        # Assert
        mock_db_session.query.assert_called_once_with(Cart)
        assert len(result) == 0


class TestProcessCarts:
    @patch("backend.domain.carts.cart_service.FileUtil")
    def test_process_new_cart(
        self,
        mock_file_util,
        cart_service,
        mock_dummy_json_api,
        mock_db_session,
        mock_product_from_cart_service,
    ):
        # Arrange
        cart_json = {"id": 1, "userId": 101}
        mock_dummy_json_api.get_carts.return_value = [[cart_json]]

        # Set up session to indicate cart doesn't exist
        mock_db_session.query.return_value.filter.return_value.count.return_value = 0

        # Act
        cart_service.process_carts()

        # Assert
        mock_db_session.query.assert_called_with(Cart)
        mock_db_session.query.return_value.filter.assert_called_once()
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_file_util.save_result_to_txt_file.assert_called_once_with(
            "carts.txt", CartDto(cart_id=1, user_id=101)
        )
        mock_product_from_cart_service.process_products_from_carts.assert_called_once_with(
            cart_json, CartDto(cart_id=1, user_id=101)
        )

    @patch("backend.domain.carts.cart_service.FileUtil")
    def test_process_existing_cart(
        self,
        mock_file_util,
        cart_service,
        mock_dummy_json_api,
        mock_db_session,
        mock_product_from_cart_service,
    ):
        # Arrange
        cart_json = {"id": 1, "userId": 101}
        mock_dummy_json_api.get_carts.return_value = [[cart_json]]

        # Set up session to indicate cart exists
        mock_db_session.query.return_value.filter.return_value.count.return_value = 1

        # Act
        cart_service.process_carts()

        # Assert
        mock_db_session.query.assert_called_with(Cart)
        mock_db_session.query.return_value.filter.assert_called_once()
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_file_util.save_result_to_txt_file.assert_not_called()
        mock_product_from_cart_service.process_products_from_carts.assert_not_called()

    @patch("backend.domain.carts.cart_service.FileUtil")
    def test_process_multiple_cart_batches(
        self,
        mock_file_util,
        cart_service,
        mock_dummy_json_api,
        mock_db_session,
        mock_product_from_cart_service,
    ):
        # Arrange
        cart1 = {"id": 1, "userId": 101}
        cart2 = {"id": 2, "userId": 102}
        batch1 = [cart1]
        batch2 = [cart2]
        mock_dummy_json_api.get_carts.return_value = [batch1, batch2]

        # First cart doesn't exist, second cart exists
        mock_db_session.query.return_value.filter.return_value.count.side_effect = [
            0,
            1,
        ]

        # Act
        cart_service.process_carts()

        # Assert
        assert mock_db_session.query.return_value.filter.call_count == 2
        assert mock_db_session.add.call_count == 1
        assert mock_db_session.commit.call_count == 1
        assert mock_file_util.save_result_to_txt_file.call_count == 1
        assert (
            mock_product_from_cart_service.process_products_from_carts.call_count == 1
        )

    @patch("backend.domain.carts.cart_service.FileUtil")
    def test_process_empty_batch(
        self,
        mock_file_util,
        cart_service,
        mock_dummy_json_api,
        mock_db_session,
        mock_product_from_cart_service,
    ):
        # Arrange
        mock_dummy_json_api.get_carts.return_value = [[]]

        # Act
        cart_service.process_carts()

        # Assert
        mock_file_util.clean_txt_file_before_processing.assert_any_call("carts.txt")
        mock_file_util.clean_txt_file_before_processing.assert_any_call(
            "products_from_carts.txt"
        )
        mock_dummy_json_api.get_carts.assert_called_once()
        mock_db_session.query.assert_not_called()
        mock_db_session.query.return_value.filter.assert_not_called()
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_file_util.save_result_to_txt_file.assert_not_called()
        mock_product_from_cart_service.process_products_from_carts.assert_not_called()
