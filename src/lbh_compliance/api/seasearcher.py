from lbh_compliance.config.settings import (
    SEASEARCHER_BASE_URL,
    API_TIMEOUT,
    SEASEARCHER_USERNAME,
    SEASEARCHER_PASSWORD,
)
from lbh_compliance.utils.loggers import get_logger

import requests
from typing import Optional, Literal


class SeaSearcherAPIClient:
    def __init__(
        self,
        logging_level: Literal["debug", "info", "warn", "error", "critical"] = "info",
    ) -> None:
        self.logger = get_logger(__name__, logging_level)
        self.logging_level: Literal["debug", "info", "warn", "error", "critical"] = (
            logging_level
        )
        self.base_url = SEASEARCHER_BASE_URL
        self.token_url = f"{self.base_url}/tokenprovider"
        self.sanctions_url = f"{self.base_url}/vesselsanctions_v2"

        # Retrieve credentials
        self.username = SEASEARCHER_USERNAME
        self.password = SEASEARCHER_PASSWORD

        self._token: Optional[str] = None
        self.session = requests.Session()

    def _get_auth_token(self) -> str:
        """
        Retrieves or refreshes the authorization token.

        Returns:
            str: The authorization token.

        Raises:
            RuntimeError: If token retrieval fails.
        """
        payload = {"username": self.username, "password": self.password}

        try:
            response = self.session.post(
                self.token_url, json=payload, timeout=API_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            if data.get("Message") == "Success":
                token = data.get("Payload")
                if not token:
                    msg = "Token received but payload is empty."
                    self.logger.error(msg)
                    raise RuntimeError(msg)
                self._token = token
                return token
            else:
                raise RuntimeError(f"Authentication failed: {data.get('Message')}")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error during token retrieval: {e}")

    def is_sanctioned(self, imo: str) -> bool:
        """
        Check if a vessel with the given IMO is sanctioned.

        Args:
            imo (str): The IMO number of the vessel (e.g., "9515802").

        Returns:
            bool: True if the vessel is sanctioned, False otherwise.

        Raises:
            RuntimeError: If the API request fails or returns an unexpected status.
        """
        token = self._get_auth_token()

        headers = {"Authorization": token, "Content-Type": "application/json"}

        params = {"vesselImo": imo}

        response = self.session.get(
            self.sanctions_url, headers=headers, params=params, timeout=API_TIMEOUT
        )

        try:
            response.raise_for_status()
            data = response.json()

            # According to the schema:
            # isSuccess: boolean
            # Data: { items: [...] }
            # If items is non-empty, the vessel is sanctioned.

            if data.get("IsSuccess"):
                items = data.get("Data", {}).get("items", [])
                return len(items) > 0
            else:
                # If IsSuccess is false but no error was raised, assume not sanctioned
                # or handle specific error codes if the API returns them in the body.
                return False

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                # Token might be expired or invalid, retry once?
                # For simplicity, we raise here.
                raise RuntimeError("Authentication failed (401). Check credentials.")
            elif response.status_code == 403:
                raise RuntimeError(
                    "Forbidden (403). Your subscription may not include this endpoint."
                )
            else:
                raise RuntimeError(
                    f"API request failed with status {response.status_code}: {e}"
                )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error: {e}")


# Example Usage:
if __name__ == "__main__":
    # Option 1: Pass credentials directly
    # client = SeaSearcherAPIClient(username="test.user@abc.com", password="password123")

    # Option 2: Use environment variables (Recommended)
    # export LLI_USERNAME="test.user@abc.com"
    # export LLI_PASSWORD="password123"
    client = SeaSearcherAPIClient()

    try:
        imo_to_check = "9515802"
        is_sanctioned = client.is_sanctioned(imo_to_check)
        print(f"Vessel {imo_to_check} is sanctioned: {is_sanctioned}")
    except Exception as e:
        print(f"Error: {e}")
