import pytest
from unittest.mock import MagicMock, patch

from backend.domain.services.product_from_cart_service import ProductFromCartService
from backend.common.models.product_from_cart_dto import ProductFromCartDto
from backend.domain.entities.product_from_cart import ProductFromCart
from backend.common.models.cart_dto import CartDto


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = None
    return session


@pytest.fixture
def product_from_cart_service(mock_db_session):
    return ProductFromCartService(mock_db_session)


class TestGetBoughtProductsFromCarts:
    def test_get_bought_products_from_carts_returns_converted_dtos(
        self, product_from_cart_service, mock_db_session
    ):
        # Arrange
        product1 = ProductFromCart(cart_id=1, product_id=10, quantity=2)
        product2 = ProductFromCart(cart_id=2, product_id=20, quantity=5)
        mock_db_session.query.return_value.all.return_value = [product1, product2]

        # Act
        result = product_from_cart_service.get_bought_products_from_carts()

        # Assert
        mock_db_session.query.assert_called_once_with(ProductFromCart)
        assert len(result) == 2
        assert all(isinstance(prod, ProductFromCartDto) for prod in result)
        assert result[0].cart_id == 1
        assert result[0].product_id == 10
        assert result[0].quantity == 2
        assert result[1].cart_id == 2
        assert result[1].product_id == 20
        assert result[1].quantity == 5

    def test_get_bought_products_from_carts_returns_empty_list_when_no_products(
        self, product_from_cart_service, mock_db_session
    ):
        # Arrange
        mock_db_session.query.return_value.all.return_value = []

        # Act
        result = product_from_cart_service.get_bought_products_from_carts()

        # Assert
        mock_db_session.query.assert_called_once_with(ProductFromCart)
        assert len(result) == 0


class TestProcessProductsFromCarts:
    @patch("backend.domain.services.product_from_cart_service.FileUtil")
    def test_process_products_from_carts_adds_new_products(
        self, mock_file_util, product_from_cart_service, mock_db_session
    ):
        # Arrange
        cart = {
            "id": 1,
            "products": [
                {"id": 10, "quantity": 2},
                {"id": 20, "quantity": 5},
            ],
        }
        cart_dto = CartDto(cart_id=1, user_id=123)

        # Act
        product_from_cart_service.process_products_from_carts(cart, cart_dto)

        # Assert
        assert mock_db_session.add.call_count == 2
        assert mock_db_session.commit.call_count == 2
        assert mock_file_util.save_result_to_txt_file.call_count == 2
        calls = [
            (
                "products_from_carts.txt",
                ProductFromCartDto(cart_id=1, product_id=10, quantity=2),
            ),
            (
                "products_from_carts.txt",
                ProductFromCartDto(cart_id=1, product_id=20, quantity=5),
            ),
        ]
        actual_calls = [
            call.args for call in mock_file_util.save_result_to_txt_file.call_args_list
        ]
        assert actual_calls == calls

    @patch("backend.domain.services.product_from_cart_service.FileUtil")
    def test_process_products_from_carts_with_no_products(
        self, mock_file_util, product_from_cart_service, mock_db_session
    ):
        # Arrange
        cart = {"id": 1, "products": []}
        cart_dto = CartDto(cart_id=1, user_id=123)

        # Act
        product_from_cart_service.process_products_from_carts(cart, cart_dto)

        # Assert
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_file_util.save_result_to_txt_file.assert_not_called()

    @patch("backend.domain.services.product_from_cart_service.FileUtil")
    def test_process_products_from_carts_with_missing_products_key(
        self, mock_file_util, product_from_cart_service, mock_db_session
    ):
        # Arrange
        cart = {"id": 1}
        cart_dto = CartDto(cart_id=1, user_id=123)

        # Act
        product_from_cart_service.process_products_from_carts(cart, cart_dto)

        # Assert
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_file_util.save_result_to_txt_file.assert_not_called()
