from lbh_compliance.config.settings import (
    PORTABLE_BASE_URL,
    API_TIMEOUT,
    PORTABLE_EMAIL,
    PORTABLE_PASSWORD,
)
from lbh_compliance.utils.loggers import get_logger

from typing import Literal, Dict, Union, List
from urllib.parse import urljoin
import requests


class PortAbleAPIClient:
    def __init__(
        self,
        logging_level: Literal["debug", "info", "warn", "error", "critical"] = "info",
    ) -> None:
        self.logger = get_logger(__name__, logging_level)
        self.base_url = PORTABLE_BASE_URL
        self.email = PORTABLE_EMAIL
        self.password = PORTABLE_PASSWORD
        self.session = requests.Session()
        self.auth_token = None

    def login(self) -> None:
        self.logger.info("Logging into PortAble")

        url = urljoin(self.base_url, f"auth/login")
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        json_data = {
            "email": self.email,
            "password": self.password,
        }
        response = self.session.post(
            url=url, headers=headers, json=json_data, timeout=API_TIMEOUT
        )
        try:
            response.raise_for_status()
        except Exception as e:
            self.logger.error(
                f"Error during connect_to_PA (response.raise_for_status): {e}",
                exc_info=True,
            )
        if not response.json()["status"]:
            self.logger.error(
                f'Error during connect_to_PA (response.json()["status"]): {response.json}',
                exc_info=True,
            )
            raise requests.exceptions.ConnectionError(response=response)
        self.auth_token = response.json()["data"]["accessToken"]
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.auth_token}",
                "accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        self.logger.info("Successful login into PortAble")

    def get_portcall(
        self, portcall_id: str
    ) -> Dict[str, Union[str, None, List, Dict, bool, int, float]]:
        url = urljoin(self.base_url, "portcall/search")
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.auth_token,
        }

        payload = {
            "filtersList": [
                {
                    "field": "status",
                    "comparison": "=",
                    "value": [
                        "Expected",
                        "Berthed",
                        "Arrived",
                        "Anchored",
                        "Sailed",
                        "Cancelled",
                    ],
                },
                {"value": [portcall_id], "comparison": "=", "field": "uniqueNumber"},
            ],
            "order": {"field": "eta", "direction": 10},
        }

        response = requests.post(
            url=url, data=payload, headers=headers, timeout=API_TIMEOUT
        )

        try:
            response.raise_for_status()
        except Exception as e:
            self.logger.error(
                f"Error during get_portcall (response.raise_for_status): {e}",
                exc_info=True,
            )
        if not response.json()["status"]:
            self.logger.error(
                f'Error during get_portcall (response.json()["status"]): {response.json}',
                exc_info=True,
            )
            raise requests.exceptions.ConnectionError(response=response)

        if response.json()["data"]["total"] == 0:
            self.logger.error(
                f"Query was successful, but portcall {portcall_id} does not exist.",
                exc_info=True,
            )
            raise requests.exceptions.ConnectionError(response=response)

        if response.json()["data"]["total"] > 1:
            self.logger.error(
                f"Query was successful, but portcall {portcall_id} is not unique.",
                exc_info=True,
            )
            raise requests.exceptions.ConnectionError(response=response)

        return response.json()["data"]["entries"][0]
