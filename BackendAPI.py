import requests
import os
import dotenv

dotenv.load_dotenv()
backend_api_url = os.getenv("BACKEND_API_URL")


class BackendError(Exception):
    ...


def find_photo(description: str, photo_amount: int, chat_id: int) -> list[str]:
    params = {
        "description": description,
        "photo_amount": photo_amount,
        "chat_id": chat_id
    }

    try:
        response = requests.get(f"{backend_api_url}/find_photo",
                                params=params)
        if response.status_code != 200:
            raise BackendError("Request to find photos failed")

    except (requests.exceptions.RequestException, BackendError):
        raise BackendError("Request to find photos failed")

    return response.json()


def process_photo(photo: bytes, file_id: str, chat_id: int) -> None:
    params = {
        "chat_id": chat_id,
        "file_id": file_id
    }
    files = {
        "photo": photo
    }

    try:
        response = requests.post(f"{backend_api_url}/process_photo",
                                 params=params,
                                 files=files)
        if response.status_code != 200:
            raise BackendError(f"Request to process photo with id {file_id} failed")

    except (requests.exceptions.RequestException, BackendError):
        raise BackendError("Request to find photos failed")


def create_chat(chat_id: int) -> None:
    try:
        params = {
            "chat_id": chat_id
        }
        response = requests.post(f"{backend_api_url}/create_chat",
                                 params=params)
        if response.status_code != 200:
            raise BackendError(f"Failed to initialize chat with chat_id {chat_id}")

    except (requests.exceptions.RequestException, BackendError):
        raise BackendError("Request to find photos failed")
