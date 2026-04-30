from lbh_compliance.config.settings import PASCAL_BASE_URL, API_TIMEOUT, PASCAL_HEADERS
from lbh_compliance.utils.loggers import get_logger

from typing import Literal, Optional, Union, List, Dict
from urllib.parse import urljoin
import requests


class PascalAPIClient:
    def __init__(
        self,
        logging_level: Literal["debug", "info", "warn", "error", "critical"] = "info",
    ) -> None:
        self.logger = get_logger(__name__, logging_level)
        self.base_url = PASCAL_BASE_URL
        self.headers = PASCAL_HEADERS

        self.session = requests.Session()

    def get_case_if_exists(
        self, name: str
    ) -> Optional[Union[List[str], Dict[str, Union[str, None, int, Dict, List]]]]:
        self.logger.info(f"Looking for case {name} in Pascal")

        url = urljoin(self.base_url, f"/api/v1/cases/searches")

        body = {
            "with": ["hitCountsPerSource"],
            "name": name,
        }

        response = self.session.post(
            url=url, headers=self.headers, json=body, timeout=API_TIMEOUT
        )

        try:
            response.raise_for_status()
        except Exception as e:
            self.logger.error(
                f"Error during get_case_if_exists (response.raise_for_status): {e}",
                exc_info=True,
            )
        if not response.json()["status"]:
            self.logger.error(
                f'Error during get_case_if_exists (response.json()["status"]): {response.json}',
                exc_info=True,
            )
            raise requests.exceptions.ConnectionError(response=response)

        if response.json()["meta"]["total"] == 0:
            # No cases found for this name
            return None

        elif response.json()["meta"]["total"] > 1:
            # More cases found with this name, more clarity needed
            pass

        else:
            # One case found, return its object
            return response.json()["data"][0]
