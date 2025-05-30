import os
from typing import Protocol


class DtoProtocol(Protocol):
    def __repr__(self) -> str: ...


class FileUtil:
    @staticmethod
    def save_result_to_txt_file(file_name: str, data: DtoProtocol) -> None:
        try:
            directory: str = "backend/data_txt"
            os.makedirs(directory, exist_ok=True)

            file_path: str = f"{directory}/{file_name}"
            with open(file_path, "a") as file:
                file.write(repr(data) + "\n")
        except Exception as e:
            print(f"An error occurred while saving to file: {e}")

    @staticmethod
    def clean_txt_file_before_processing(file_name: str) -> None:
        try:
            directory: str = "backend/data_txt"
            file_path: str = f"{directory}/{file_name}"
            with open(file_path, "w") as file:
                file.write("")
        except Exception as e:
            print(f"An error occurred while cleaning the file: {e}")
