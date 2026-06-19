from typing import List, Dict, Literal
from PIL import Image
from PyPDF2 import PdfReader
import re
import io
import warnings
import pytesseract

from lbh_compliance.utils.loggers import get_logger


class BLReader:
    def __init__(
        self,
        bl_bytes: bytes,
        logging_level: Literal["debug", "info", "warn", "error", "critical"] = "info",
    ) -> None:
        self.logger = get_logger(__name__, logging_level)
        self.bl_bytes: bytes = bl_bytes

    def get_parties_from_bl(self) -> Dict[str, str]:
        if self.bl_bytes[:4] == b"%PDF":
            return self._extract_txt_from_pdf(self.bl_bytes)

        elif self.bl_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            return self._extract_from_png_bytes(self.bl_bytes)

        msg = "BL cannot be read."
        self.logger.warning(msg)
        warnings.warn(msg)
        return {}

    def _extract_txt_from_pdf(self, file_bytes: bytes) -> Dict[str, str]:
        reader = PdfReader(io.BytesIO(file_bytes))

        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        return self._extract_parties_from_ocr_text(text)

    def _extract_parties_from_ocr_text(self, text: str) -> Dict[str, str]:
        text = text.replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n+", "\n", text).strip()
        lines = text.split("\n")

        def find_value(labels: List[str]):
            """
            Finds first line after a label (Shipper, Consignee, Notify, etc.)
            """
            nonlocal lines
            for i, line in enumerate(lines):
                for label in labels:
                    if re.search(rf"\b{label}\b", line, re.IGNORECASE):
                        # Look ahead for first non-empty line
                        for j in range(i + 1, min(i + 6, len(lines))):
                            value = lines[j].strip()

                            if not value:
                                continue

                            # Stop if next section starts
                            if re.match(r"[A-Z][A-Za-z ]+$", value):
                                continue

                            return value
            return None

        shipper = find_value(["Shipper", "Consignor"])
        consignee = find_value(["Consignee"])
        notify = find_value(["Notify address", "Notify"])

        # Normalize consignee ("to the order of ...")
        if consignee:
            consignee = re.sub(r"to the order of ", "", consignee, flags=re.IGNORECASE)

        parties = {
            shipper: "Cargo Shipper",
            consignee: "Cargo Consignee",
            notify: "Notify",
        }

        return {key: val for key, val in parties.items() if key}

    def _extract_from_png_bytes(self, file_bytes: bytes) -> Dict[str, str]:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image, config="--oem 3 --psm 6")
        return self._extract_parties_from_ocr_text(text)
