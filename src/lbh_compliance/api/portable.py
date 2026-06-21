from lbh_compliance.config.settings import (
    PORTABLE_BASE_URL,
    API_TIMEOUT,
    PORTABLE_EMAIL,
    PORTABLE_PASSWORD,
)
from lbh_compliance.utils.loggers import get_logger
from lbh_compliance.utils.dtypes import (
    PortAbleResponse,
    PortAbleResponseAttachmentslistItem,
)
from lbh_compliance.config.patterns import BL_PATTERN
from lbh_compliance.tools.bl import BLReader

from typing import Literal, TypedDict, Optional, List, Dict, Set
from urllib.parse import urljoin
import requests
import html
import warnings
import datetime as dt


class FilteredPortAbleData(TypedDict):
    bl: Optional[bytes]
    parties: List[str]


class PortAbleAPIClient:
    def __init__(
        self,
        logging_level: Literal["debug", "info", "warn", "error", "critical"] = "info",
    ) -> None:
        self.logger = get_logger(__name__, logging_level)
        self.logging_level: Literal["debug", "info", "warn", "error", "critical"] = (
            logging_level
        )
        self.base_url = PORTABLE_BASE_URL
        self.email = PORTABLE_EMAIL
        self.password = PORTABLE_PASSWORD
        self.session = requests.Session()
        self.auth_token = None

        # Data regarding the search query
        self.parties: Dict[str, Set[str]] = {}
        self.other_parties: Set[str] = set()
        self.attachments_dict: Dict[str, str] = {}

        self.vessel_name: str = ""
        self.vessel_imo: str = ""

    def login(self) -> None:
        """
        Log into PortAble Agent, this only needs to be done once per instance.
        The session and authentication tokens are stored in the instance.

        Raises:
            requests.exceptions.ConnectionError: If there is any other status than 200.
            requests.exceptions.RequestException: If the `status` key is False in the JSON response.
            KeyError: If the `accessToken` key does not exist in the JSON response.
        """
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
            raise requests.exceptions.ConnectionError(response=response)
        if not response.json()["status"]:
            self.logger.error(
                f'Error during connect_to_PA (response.json()["status"]): {response.json}',
                exc_info=True,
            )
            raise requests.exceptions.RequestException(response=response)

        response_data = response.json()["data"]
        if "accessToken" not in response_data.keys():
            msg = f"'accessToken' not in response data ({response_data})"
            self.logger.error(msg)
            raise KeyError(msg)

        self.auth_token = response.json()["data"]["accessToken"]
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.auth_token}",
                "accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        self.logger.info("Successful login into PortAble")

    def find_parties_from_portcall(self, portcall_num: str) -> None:
        """
        Finds all the parties and attachments in a portcall and stores them in the following attributes:
        - `parties`: Dict[str, Set[str]] - {"party_name": {"role_1", "role_2"}}
        - `other_parties`: Set[str] - {"party_1", "party_2"}
        - `attachments_dict`: Dict[str, str] - {"attachment_1.pdf": "https://download.example.com/attachment_1"}

        Args:
            portcall_num (str): The portcall ID to look for, examples: UY260022, NL240190, CN250453

        Raises:
            AttributeError: if there are no parties found for this portcall ID
        """
        # Clear this data when rerunning the API client
        self.parties: Dict[str, Set[str]] = {}
        self.other_parties: Set[str] = set()
        self.attachments_dict: Dict[str, str] = {}

        pc_id = self.get_portcall_search_id(portcall_num)

        response = self.get_portcall_data(pc_id)
        self._store_filtered_data_in_instance(response)
        bl_bytes = self._get_bl(response["attachmentsList"])

        if bl_bytes is not None:
            reader = BLReader(bl_bytes, self.logging_level)
            bl_parties = reader.get_parties_from_bl()
            for party, role in bl_parties.items():
                if party in self.parties.keys():
                    self.parties[party].add(role)
                else:
                    self.parties[party] = {role}

        if len(self.parties.keys()) + len(self.other_parties) == 0:
            msg = f"No parties found in PortAble for portcall {portcall_num}"
            self.logger.error(msg)
            raise AttributeError(msg)

    def get_portcall_search_id(self, portcall_num: str) -> str:
        """
        Get the portcall ID based on the portcall number

        Args:
            portcall_num (str): The portcall number to look for, examples: UY260022, NL240190, CN250453

        Raises:
            requests.exceptions.ConnectionError: If there is any other status than 200.
            requests.exceptions.RequestException: If the `status` key is False in the JSON response.
            ValueError: If the portcall ID does not exist
            LookupError: If the portcall ID returns multiple portcalls
            KeyError: If the JSON response does not have an ID key

        Returns:
            str: The portcall ID, examples: t4tiLfK7CGt9e4raEzwA, xvIq4XmgW7QnRCpkSejR
        """
        self.logger.info(f"Looking for {portcall_num} in PortAble")

        url = urljoin(self.base_url, "portcall/search")

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
                {"value": [portcall_num], "comparison": "=", "field": "uniqueNumber"},
            ],
            "order": {"field": "eta", "direction": 10},
        }

        response = self.session.post(url=url, json=payload, timeout=API_TIMEOUT)

        try:
            response.raise_for_status()
        except Exception as e:
            self.logger.error(
                f"Error during get_portcall (response.raise_for_status): {e}",
                exc_info=True,
            )
            raise requests.exceptions.ConnectionError(response=response)
        if not response.json()["status"]:
            self.logger.error(
                f'Error during get_portcall (response.json()["status"]): {response.json}',
                exc_info=True,
            )
            raise requests.exceptions.RequestException(response=response)

        if response.json()["data"]["total"] == 0:
            msg = f"Query was successful, but portcall {portcall_num} does not exist."
            self.logger.error(
                msg,
                exc_info=True,
            )
            raise ValueError(msg)

        if response.json()["data"]["total"] > 1:
            msg = f"Query was successful, but portcall {portcall_num} is not unique."
            self.logger.error(
                msg,
                exc_info=True,
            )
            raise LookupError(msg)

        pc = response.json()["data"]["entries"][0]
        if pc.get("id") is not None:

            cargo_consignee: List[str] = pc["cargoConsignee"]
            cargo_shipper: List[str] = pc["cargoShipper"]

            for txt in cargo_consignee:
                if txt not in ["", "-", " - ", None] and txt not in self.parties.keys():
                    self.parties[txt] = {"Cargo Consignee"}

            for txt in cargo_shipper:
                if txt not in ["", "-", " - ", None] and txt not in self.parties.keys():
                    self.parties[txt] = {"Cargo Shipper"}
                elif txt not in ["", "-", " - ", None] and txt in self.parties.keys():
                    self.parties[txt].add("Cargo Shipper")

            self.logger.info(f"Portcall {portcall_num} found and extracted ID")
            return pc["id"]

        msg = f"No ID found for portcall {portcall_num}"
        self.logger.error(msg)
        raise KeyError(msg)

    def get_portcall_data(self, portcall_id: str) -> PortAbleResponse:
        """_summary_

        Args:
            portcall_id (str): The unique ID for the portcall (found in the URL), such as xvIq4XmgW7QnRCpkSejR

        Raises:
            requests.exceptions.ConnectionError: If there is any other status than 200.
            requests.exceptions.RequestException: If the `status` key is False in the JSON response.

        Returns:
            PortAbleResponse: A Dict-like object containing the JSON response
        """
        url = urljoin(self.base_url, f"portcall/{portcall_id}")
        response = self.session.get(url=url, timeout=API_TIMEOUT)

        try:
            response.raise_for_status()
        except Exception as e:
            self.logger.error(
                f"Error during get_portcall (response.raise_for_status): {e}",
                exc_info=True,
            )
            raise requests.exceptions.ConnectionError(response=response)
        if not response.json()["status"]:
            self.logger.error(
                f'Error during get_portcall (response.json()["status"]): {response.json()}',
                exc_info=True,
            )
            raise requests.exceptions.RequestException(response=response)

        return response.json()["data"]

    def _store_filtered_data_in_instance(self, response: PortAbleResponse) -> None:
        """
        Stores the necessary data from the JSON in the instance attributes.
        - `parties`: Dict[str, Set[str]] - {"party_name": {"role_1", "role_2"}}
        - `other_parties`: Set[str] - {"party_1", "party_2"}
        - `attachments_dict`: Dict[str, str] - {"attachment_1.pdf": "https://download.example.com/attachment_1"}


        Args:
            response (PortAbleResponse): The Dict-like object containing the JSON response
        """
        principal_name = response["principal"]["name"]
        if principal_name and principal_name not in self.parties.keys():
            self.parties[principal_name] = {"Principal"}
        elif principal_name and principal_name in self.parties.keys():
            self.parties[principal_name].add("Principal")

        # After some testing, it appears as if husbandry is optional
        if response.get("husbandry") is not None:
            husbandry_name = response["husbandry"]["name"]
            if husbandry_name and husbandry_name not in self.parties.keys():
                self.parties[husbandry_name] = {"Husbandry"}
            elif husbandry_name and husbandry_name in self.parties.keys():
                self.parties[husbandry_name].add("Husbandry")

        da_owner_name = response["daOwner"]["name"]
        if da_owner_name and da_owner_name not in self.parties.keys():
            self.parties[da_owner_name] = {"DA Owner"}
        elif da_owner_name and da_owner_name in self.parties.keys():
            self.parties[da_owner_name].add("DA Owner")

        if other_parties_list := response["otherPartiesList"]:
            for party in other_parties_list:
                if (party["name"] not in self.parties.keys()) and (
                    not party["name"].startswith("LBH ")
                ):
                    self.other_parties.add(party["name"])

        if portable_parties_list := response["portablePartiesList"]:
            for party in portable_parties_list:
                if (party["name"] not in self.parties.keys()) and (
                    not party["name"].startswith("LBH ")
                ):
                    self.other_parties.add(party["name"])

        # We store vessel data seperately
        self.vessel_name = response["vessel"]["name"]
        self.vessel_imo = response["vessel"]["imo"]

    def _download_bl_file(self, url: str) -> bytes:
        """
        This downloads a BL file from the Google Drive URL

        Args:
            url (str): The Google Drive URL with the download code

        Raises:
            requests.exceptions.ConnectionError: If the status code is not 200

        Returns:
            bytes: The file contents as bytes
        """
        url = html.unescape(url)

        response = requests.get(url)
        if response.status_code != 200:
            msg = f"Failed to download BL: {response.text}"
            self.logger.error(msg)
            raise requests.exceptions.ConnectionError(msg)

        return response.content

    def _get_bl(
        self, attachments: List[PortAbleResponseAttachmentslistItem]
    ) -> Optional[bytes]:
        """
        Tries to look for the BL in the attachments list using a RegEx.
        If multiple are found, the most recent one is taken as BL.

        Args:
            attachments (List[PortAbleResponseAttachmentslistItem]): A list of Dict-like objects containing the attachments data.

        Returns:
            Optional[bytes]: The content of the BL as bytes if found, else None.
        """
        if len(attachments) == 0:
            msg = "No attachments found for this Portcall"
            self.logger.warning(msg)
            warnings.warn(msg)
            return None

        bl_url = ""
        bl_date = dt.datetime(1970, 1, 1)
        bl_name = ""
        attachment_names: List[str] = []

        for item in attachments:
            # Store everything in the attachments_dict attribute
            self.attachments_dict[item["filename"]] = item["url"]

            attachment_names.append(item["filename"])
            # Check if BL is in attachments
            match = BL_PATTERN.search(item["filename"])
            if match:
                self.logger.info(
                    f"{item["filename"]} was deduced to be (one of) the BLs."
                )
                # Check for the most recent BL
                # Sometimes there are multiple BLs (when something updated/someone signed it)
                if dt.datetime.fromisoformat(item["createdAt"]) > bl_date:
                    bl_name = item["filename"]
                    bl_url = item["url"]
            else:
                self.logger.debug(f"No match in '{item["filename"]}'")

        if bl_url != "":
            # At this point, we have found the most recent BL
            self.logger.info(f"BL found: {bl_name}")
            return self._download_bl_file(bl_url)

        msg = f"No BL found in {attachment_names}!"
        self.logger.warning(msg)
        warnings.warn(msg)
        return None
