from abc import ABC, abstractmethod


class UserServiceInterface(ABC):
    @abstractmethod
    def process_users(self) -> None:
        pass

    @abstractmethod
    def get_all_users(self):
        pass
