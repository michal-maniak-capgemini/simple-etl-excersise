from typing import Any, Dict, List

from sqlalchemy.orm import Session

from backend.common.models.user_dto import UserDto
from backend.common.utils.coordinates_util import CoordinatesUtil
from backend.common.utils.file_util import FileUtil
from backend.common.utils.logger import logger
from backend.domain.entities.user import User
from backend.interfaces.user_service_interface import UserServiceInterface
from backend.interfaces.dummy_json_api_interface import DummyJSONApiInterface


class UserService(UserServiceInterface):
    __USERS_TXT: str = "users.txt"

    def __init__(self, dummy_json_api: DummyJSONApiInterface, db_session: Session):
        self.__dummy_json_api: DummyJSONApiInterface = dummy_json_api
        self.__db_session: Session = db_session

    def get_all_users(self) -> List[UserDto]:
        with self.__db_session:
            logger.info("Fetching all users from DB")
            users_entities = self.__db_session.query(User).all()
            return [UserDto.model_validate(user) for user in users_entities]

    def process_users(self) -> None:
        FileUtil.clean_txt_file_before_processing(self.__USERS_TXT)
        for users_batch in self.__dummy_json_api.get_users():
            self.__process_single_batch_of_users(users_batch)

    def __process_single_batch_of_users(self, users: List[Dict[str, Any]]) -> None:
        for user in users:
            user_id: int = user.get("id")
            logger.info(f"Processing user with ID: {user_id}")
            is_user_in_db: bool = self.__is_user_in_db(user)
            if not is_user_in_db:
                logger.info(f"User with ID: {user_id} is not in DB, processing...")
                country: str = self.__get_country_from_user(user)
                user_dto: UserDto = UserDto(
                    first_name=user.get("firstName"),
                    last_name=user.get("lastName"),
                    email=user.get("email"),
                    age=user.get("age"),
                    birth_date=user.get("birthDate"),
                    street=user.get("address").get("address"),
                    city=user.get("address").get("city"),
                    country=country,
                    user_id=user_id,
                )
                self.__add_user_to_db(user_dto)
                self.__add_user_to_txt(user_dto)
            else:
                logger.info(
                    f"User with ID: {user_id} already exists in DB, skipping..."
                )

    def __is_user_in_db(self, user: Dict[str, Any]) -> bool:
        email: str = user.get("email")
        if email:
            with self.__db_session:
                logger.info(f"Checking if user with email: {email} exists in DB")
                count: int = (
                    self.__db_session.query(User).filter(User.email == email).count()
                )

                return count > 0
        else:
            logger.warning("User email is None, skipping check")
            return True

    @staticmethod
    def __get_country_from_user(user: Dict[str, Any]) -> str:
        logger.info(
            f"Processing country name by coordinates: {user.get('address').get('coordinates')}"
        )
        latitude: str = user.get("address").get("coordinates").get("lat")
        longitude: str = user.get("address").get("coordinates").get("lng")
        country: str = CoordinatesUtil.get_country_by_coordinates(latitude, longitude)
        return country

    def __add_user_to_db(self, user_dto: UserDto) -> None:
        user_entity = User(
            first_name=user_dto.first_name,
            last_name=user_dto.last_name,
            email=user_dto.email,
            age=user_dto.age,
            birth_date=user_dto.birth_date,
            street=user_dto.street,
            city=user_dto.city,
            country=user_dto.country,
            user_id=user_dto.user_id,
        )

        with self.__db_session:
            logger.info(f"Adding user to DB: {user_entity}")
            self.__db_session.add(user_entity)
            self.__db_session.commit()

    def __add_user_to_txt(self, user_dto: UserDto) -> None:
        logger.info(f"Adding user to the txt file: {user_dto}")
        FileUtil.save_result_to_txt_file(self.__USERS_TXT, user_dto)
