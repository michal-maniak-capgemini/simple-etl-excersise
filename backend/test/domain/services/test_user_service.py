from unittest.mock import MagicMock, Mock, patch

import pytest

from backend.common.models.user_dto import UserDto
from backend.domain.entities.user import User
from backend.domain.services.user_service import UserService
from backend.interfaces.dummy_json_api_interface import DummyJSONApiInterface


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
def user_service(mock_db_session, mock_dummy_json_api):
    """Fixture for creating a UserService instance with mocked dependencies"""
    return UserService(mock_dummy_json_api, mock_db_session)


class TestGetAllUsers:
    def test_get_all_users_returns_converted_dtos(self, user_service, mock_db_session):
        # Arrange
        user1 = User(
            first_name="John",
            last_name="Doe",
            email="example@email.com",
            age=30,
            birth_date="1995-01-01",
            street="123 Main St",
            city="Anytown",
            country="USA",
            user_id=234,
        )

        user2 = User(
            first_name="Amy",
            last_name="Black",
            email="myexample@email.com",
            age=25,
            birth_date="2000-07-17",
            street="My Normal St",
            city="Big City",
            country="Hungary",
            user_id=12,
        )

        mock_db_session.query.return_value.all.return_value = [user1, user2]

        # Act
        result = user_service.get_all_users()

        # Assert
        mock_db_session.query.assert_called_once_with(User)
        assert len(result) == 2
        assert all(isinstance(user, UserDto) for user in result)
        assert result[0].first_name == "John"
        assert result[0].last_name == "Doe"
        assert result[0].email == "example@email.com"
        assert result[0].age == 30
        assert result[0].birth_date == "1995-01-01"
        assert result[0].street == "123 Main St"
        assert result[0].city == "Anytown"
        assert result[0].country == "USA"
        assert result[0].user_id == 234
        assert result[1].first_name == "Amy"
        assert result[1].last_name == "Black"
        assert result[1].email == "myexample@email.com"
        assert result[1].age == 25
        assert result[1].birth_date == "2000-07-17"
        assert result[1].street == "My Normal St"
        assert result[1].city == "Big City"
        assert result[1].country == "Hungary"
        assert result[1].user_id == 12

    def test_get_all_users_returns_empty_list_when_no_users(
        self, user_service, mock_db_session
    ):
        # Arrange
        mock_db_session.query.return_value.all.return_value = []

        # Act
        result = user_service.get_all_users()

        # Assert
        mock_db_session.query.assert_called_once_with(User)
        assert len(result) == 0


class TestProcessUsers:
    @patch("backend.domain.services.user_service.FileUtil")
    @patch("backend.domain.services.user_service.CoordinatesUtil")
    def test_process_new_user(
        self,
        mock_coordinates_util,
        mock_file_util,
        user_service,
        mock_dummy_json_api,
        mock_db_session,
    ):
        # Arrange
        user_json = {
            "id": 1,
            "firstName": "John",
            "lastName": "Doe",
            "email": "example@email.com",
            "age": 30,
            "birthDate": "1995-01-01",
            "address": {
                "address": "123 Main St",
                "city": "Anytown",
                "coordinates": {"lat": "40.7128", "lng": "-74.0060"},
            },
        }
        mock_dummy_json_api.get_users.return_value = [[user_json]]
        mock_coordinates_util.get_country_by_coordinates.return_value = "USA"

        mock_db_session.query.return_value.filter.return_value.count.return_value = 0

        # Act
        user_service.process_users()

        # Assert
        user_dto = UserDto(
            first_name="John",
            last_name="Doe",
            email="example@email.com",
            age=30,
            birth_date="1995-01-01",
            street="123 Main St",
            city="Anytown",
            country="USA",
            user_id=1,
        )

        mock_db_session.query.assert_called_with(User)
        mock_db_session.query.return_value.filter.assert_called_once()
        mock_db_session.query.return_value.filter.return_value.count.assert_called_once()
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_file_util.save_result_to_txt_file.assert_called_once_with(
            "users.txt", user_dto
        )
        mock_coordinates_util.get_country_by_coordinates.assert_called_once_with(
            "40.7128", "-74.0060"
        )

    @patch("backend.domain.services.user_service.FileUtil")
    @patch("backend.domain.services.user_service.CoordinatesUtil")
    def test_process_existing_user(
        self,
        mock_coordinates_util,
        mock_file_util,
        user_service,
        mock_dummy_json_api,
        mock_db_session,
    ):
        # Arrange
        user_json = {
            "id": 1,
            "firstName": "John",
            "lastName": "Doe",
            "email": "example@email.com",
            "age": 30,
            "birthDate": "1995-01-01",
            "address": {
                "address": "123 Main St",
                "city": "Anytown",
                "coordinates": {"lat": "40.7128", "lng": "-74.0060"},
            },
        }
        mock_dummy_json_api.get_users.return_value = [[user_json]]
        mock_coordinates_util.get_country_by_coordinates.return_value = "USA"

        mock_db_session.query.return_value.filter.return_value.count.return_value = 1

        # Act
        user_service.process_users()

        # Assert
        mock_db_session.query.assert_called_with(User)
        mock_db_session.query.return_value.filter.assert_called_once()
        mock_db_session.query.return_value.filter.return_value.count.assert_called_once()
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_file_util.save_result_to_txt_file.assert_not_called()
        mock_coordinates_util.get_country_by_coordinates.assert_not_called()

    @patch("backend.domain.services.user_service.FileUtil")
    @patch("backend.domain.services.user_service.CoordinatesUtil")
    def test_process_multiple_user_batches(
        self,
        mock_coordinates_util,
        mock_file_util,
        user_service,
        mock_dummy_json_api,
        mock_db_session,
    ):
        # Arrange
        user1_json = {
            "id": 1,
            "firstName": "John",
            "lastName": "Doe",
            "email": "example@email.com",
            "age": 30,
            "birthDate": "1995-01-01",
            "address": {
                "address": "123 Main St",
                "city": "Anytown",
                "coordinates": {"lat": "40.7128", "lng": "-74.0060"},
            },
        }
        user2_json = {
            "id": 2,
            "firstName": "Amy",
            "lastName": "Black",
            "email": "myexample@email.com",
            "age": 25,
            "birthDate": "2000-07-17",
            "address": {
                "address": "My Normal St",
                "city": "Big City",
                "coordinates": {"lat": "38.1123", "lng": "-5.0088"},
            },
        }
        batch1 = [user1_json]
        batch2 = [user2_json]

        mock_dummy_json_api.get_users.return_value = [batch1, batch2]
        mock_coordinates_util.get_country_by_coordinates.side_effect = [
            "USA",
            "Hungary",
        ]

        mock_db_session.query.return_value.filter.return_value.count.side_effect = [
            0,
            0,
        ]

        # Act
        user_service.process_users()

        # Assert
        assert mock_db_session.query.return_value.filter.call_count == 2
        assert mock_db_session.add.call_count == 2
        assert mock_db_session.commit.call_count == 2
        assert mock_file_util.save_result_to_txt_file.call_count == 2
        assert mock_coordinates_util.get_country_by_coordinates.call_count == 2

    @patch("backend.domain.services.user_service.FileUtil")
    @patch("backend.domain.services.user_service.CoordinatesUtil")
    def test_process_multiple_user_batches(
        self,
        mock_coordinates_util,
        mock_file_util,
        user_service,
        mock_dummy_json_api,
        mock_db_session,
    ):
        # Arrange
        mock_dummy_json_api.get_users.return_value = [[]]

        # Act
        user_service.process_users()

        # Assert
        mock_file_util.clean_txt_file_before_processing.assert_any_call("users.txt")
        mock_dummy_json_api.get_users.assert_called_once()
        mock_db_session.query.assert_not_called()
        mock_db_session.query.return_value.filter.assert_not_called()
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_file_util.save_result_to_txt_file.assert_not_called()
        mock_coordinates_util.get_country_by_coordinates.assert_not_called()
