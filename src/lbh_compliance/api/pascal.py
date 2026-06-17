from lbh_compliance.config.settings import PASCAL_BASE_URL, API_TIMEOUT, PASCAL_HEADERS
from lbh_compliance.utils.loggers import get_logger
from lbh_compliance.utils.dtypes import PascalResponse

from typing import Literal, Optional, Tuple, List
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
    ) -> Tuple[Optional[PascalResponse], Optional[str]]:
        self.logger.info(f"Looking for case {name} in Pascal")

        url = urljoin(self.base_url, f"/api/v1/cases/searches")

        body = {
            "with": ["hitCountsPerSource"],
            "name": name,
            "allow_duplicate_conversion": True,
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

        if response.json()["meta"]["total"] == 0:
            # No cases found for this name

            msg = f"No case in pascal for '{name}'"
            self.logger.warning(msg)
            return (None, msg)

        elif response.json()["meta"]["total"] > 1:
            filtered_cases: List[PascalResponse] = []

            # Delete archived cases
            for case_num in range(response.json()["meta"]["total"]):
                case_status = response.json()["data"][case_num]["status"]
                if case_status not in ["Archived", "On hold", "Preview"]:
                    filtered_cases.append(response.json()["data"][case_num])

            if len(filtered_cases) == 0:
                # No valid cases found for this name

                msg = f"This case for '{name}' is archived in Pascal"
                self.logger.warning(msg)
                return (None, msg)

            elif len(filtered_cases) == 1:
                # Only one case is leftover, we can simply use this
                return filtered_cases[0], None

            # More valid cases found with this name, more clarity needed
            urls: List[str] = []

            for i, case in enumerate(filtered_cases):
                case_uuid = case["uuid"]
                urls.append(
                    f'<a href="https://app.pascal.vartion.com/#/cases/{case_uuid}" target="_blank">CASE {i + 1}</a>'
                )

            msg = f"Multiple cases found for '{name}': {", ".join(urls)}"
            self.logger.warning(msg)
            return (None, msg)

        else:
            # One case found, return its object
            return response.json()["data"][0], None

    def get_sanctions(self, data: PascalResponse) -> Tuple[Literal[0, 1, 2], str]:
        """This function finds whether or not the party is sanctioned, and returns the URL.
        - 0 corresponds to "No sanctions in Pascal"
        - 1 corresponds to "Unresolved sanctions in Pascal"
        - 2 corresponds to "Sanctions found in Pascal"

        Args:
            data (PascalResponse): The JSON response of the Pascal API

        Returns:
            Tuple[Literal[0, 1, 2], str]: {0: "No sanctions", 1: "Unresolved sanctions", 2: "Sanctions found"} and the URL.
        """
        hits = data["hit_counts"]
        url = f'<a href="https://app.pascal.vartion.com/#/cases/{data["uuid"]}" target="_blank" align="right">View case in Pascal</a>'
        if hits["positive"]["sanctions"] > 0:
            return 2, url
        elif hits["unresolved"]["sanctions"] > 0:
            return 1, url
        else:
            return 0, url
