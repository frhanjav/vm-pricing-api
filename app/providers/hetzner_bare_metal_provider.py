import logging
import re
import json
import base64
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime
from typing import Any, List, Optional
import asyncio

from app.api.schemas import VMInstance
from app.core.config import settings
from .base_provider import BaseProvider

logger = logging.getLogger(__name__)


class HetznerBareMetalProvider(BaseProvider):
    def __init__(self):
        super().__init__("Hetzner Bare Metal")
        self.base_url = "https://robot-ws.your-server.de"

    def _parse_vcpus(self, text: str) -> int:
        lower = text.lower()
        patterns = [
            (r"(\d+)\s*[- ]?core", 1),
            (r"(\d+)\s*x\s*core", 1),
            (r"(\d+)\s*x\s*cpu", 1),
        ]

        for pattern, multiplier in patterns:
            match = re.search(pattern, lower)
            if match:
                return int(match.group(1)) * multiplier

        if "single-core" in lower:
            return 1
        if "dual-core" in lower:
            return 2
        if "quad-core" in lower:
            return 4
        if "hexa-core" in lower:
            return 6
        if "octa-core" in lower:
            return 8

        return 0

    def _parse_memory_gb(self, description_lines: List[str]) -> Optional[float]:
        for line in description_lines:
            match = re.search(r"(\d+(?:\.\d+)?)\s*GB.*RAM", line, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_storage_line(self, description_lines: List[str]) -> str:
        for line in description_lines:
            if re.search(r"\b(SSD|HDD|NVMe|SATA)\b", line, re.IGNORECASE):
                return line
        return ""

    def _parse_storage_gb(self, storage_line: str) -> int:
        if not storage_line:
            return 0

        match = re.search(
            r"(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*(TB|GB)",
            storage_line,
            re.IGNORECASE,
        )
        if not match:
            return 0

        count = int(match.group(1))
        size = float(match.group(2))
        unit = match.group(3).upper()

        total = count * size
        if unit == "TB":
            total *= 1024

        return int(total)

    def _parse_storage_type(self, storage_line: str) -> str:
        if not storage_line:
            return "Unknown"

        lower = storage_line.lower()
        if "nvme" in lower:
            return "NVMe"
        if "ssd" in lower:
            return "SSD"
        if "hdd" in lower:
            return "HDD"
        if "sata" in lower:
            return "SATA"
        return "Unknown"

    def _parse_network_performance(self, description_lines: List[str]) -> Optional[str]:
        for line in description_lines:
            if re.search(r"(gbit|mbit)", line, re.IGNORECASE):
                return line.strip()
        return None

    def _build_vm_instances_from_product(self, product: dict[str, Any], currency: str) -> List[VMInstance]:
        instances: List[VMInstance] = []

        product_id = product.get("id")
        product_name = product.get("name")
        description = product.get("description") or []
        prices = product.get("prices") or []

        description_text = " ".join(description)
        storage_line = self._extract_storage_line(description)

        instance_name = product_id or product_name or "hetzner-bare-metal"
        instance_family = re.match(r"[A-Za-z]+", str(product_id or ""))

        vcpus = self._parse_vcpus(description_text)
        memory_gb = self._parse_memory_gb(description)
        storage_gb = self._parse_storage_gb(storage_line)
        storage_type = self._parse_storage_type(storage_line)
        network_performance = self._parse_network_performance(description)

        for price_item in prices:
            location = price_item.get("location") or "Unknown"
            price = price_item.get("price") or {}

            monthly_cost = float(price.get("net", 0) or 0)
            hourly_cost = float(price.get("hourly_net", 0) or 0)

            instances.append(
                VMInstance(
                    instance_name=str(instance_name),
                    provider=self.provider_name,
                    region=str(location),
                    vcpus=vcpus,
                    memory_gb=memory_gb,
                    storage_gb=storage_gb,
                    storage_type=storage_type,
                    hourly_cost=hourly_cost,
                    monthly_cost=monthly_cost,
                    currency=currency,
                    instance_family=instance_family.group(0) if instance_family else "Dedicated",
                    network_performance=network_performance,
                    last_updated=datetime.utcnow(),
                )
            )

        return instances

    async def _get_endpoint(self, path: str) -> Any:
        auth_header = base64.b64encode(
            f"{settings.HETZNER_ROBOT_USERNAME}:{settings.HETZNER_ROBOT_PASSWORD}".encode("utf-8")
        ).decode("utf-8")

        def _request():
            request = Request(f"{self.base_url}{path}")
            request.add_header("Authorization", f"Basic {auth_header}")
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))

        return await asyncio.to_thread(_request)

    async def fetch_data(self) -> List[VMInstance]:
        if not settings.HETZNER_ROBOT_USERNAME or not settings.HETZNER_ROBOT_PASSWORD:
            logger.warning(
                "Hetzner Robot credentials not configured. Skipping Hetzner Bare Metal refresh."
            )
            return []

        instances: List[VMInstance] = []

        try:
            currency_payload = await self._get_endpoint("/order/currency")
        except HTTPError as exc:
            if exc.code == 401:
                logger.error(
                    "Hetzner Robot authentication failed (401). Use Robot webservice username/password, not Hetzner Cloud API token."
                )
                return []
            if exc.code == 403:
                logger.error(
                    "Hetzner Robot access denied (403). Ensure Webservice 'Server ordering' API access is enabled in Robot settings."
                )
                return []
            raise

        currency = str(currency_payload.get("currency", "EUR"))

        standard_products = await self._get_endpoint("/order/server/product")
        for item in standard_products:
            product = item.get("product", {})
            instances.extend(self._build_vm_instances_from_product(product, currency))

        if settings.HETZNER_INCLUDE_SERVER_MARKET:
            market_products = await self._get_endpoint("/order/server_market/product")
            for item in market_products:
                product = item.get("product", {})
                instances.extend(self._build_vm_instances_from_product(product, currency))

        return instances
