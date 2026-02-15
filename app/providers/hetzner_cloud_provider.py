import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Any, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.api.schemas import VMInstance
from app.core.config import settings
from .base_provider import BaseProvider

logger = logging.getLogger(__name__)


class HetznerCloudProvider(BaseProvider):
    def __init__(self):
        super().__init__("Hetzner Cloud")
        self.base_url = "https://api.hetzner.cloud/v1"

    def _request_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        query = f"?{urlencode(params)}" if params else ""
        request = Request(f"{self.base_url}{path}{query}")
        request.add_header("Authorization", f"Bearer {settings.HETZNER_CLOUD_API_TOKEN}")
        request.add_header("Content-Type", "application/json")

        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    async def _get_server_types(self) -> list[dict[str, Any]]:
        server_types: list[dict[str, Any]] = []
        page = 1

        while True:
            payload = await asyncio.to_thread(
                self._request_json,
                "/server_types",
                {"page": page, "per_page": 50},
            )

            server_types.extend(payload.get("server_types", []))
            pagination = payload.get("meta", {}).get("pagination", {})
            next_page = pagination.get("next_page")
            if not next_page:
                break
            page = int(next_page)

        return server_types

    async def _get_currency(self) -> str:
        payload = await asyncio.to_thread(self._request_json, "/pricing")
        return str(payload.get("pricing", {}).get("currency", "EUR"))

    def _instance_family(self, instance_name: str) -> str:
        match = re.match(r"[A-Za-z]+", instance_name)
        return match.group(0) if match else "General"

    async def fetch_data(self) -> List[VMInstance]:
        if not settings.HETZNER_CLOUD_API_TOKEN:
            logger.warning("Hetzner Cloud API token not configured. Skipping Hetzner Cloud refresh.")
            return []

        data = await self._get_server_types()
        currency = await self._get_currency()
        instances: list[VMInstance] = []

        for item in data:
            prices = item.get("prices", [])
            for price in prices:
                price_hourly = price.get("price_hourly", {})
                price_monthly = price.get("price_monthly", {})

                hourly_net = float(price_hourly.get("net", 0) or 0)
                monthly_net = float(price_monthly.get("net", 0) or 0)

                instances.append(
                    VMInstance(
                        instance_name=str(item.get("name", "unknown")),
                        provider=self.provider_name,
                        region=str(price.get("location", "unknown")),
                        vcpus=int(item.get("cores", 0) or 0),
                        memory_gb=float(item.get("memory", 0) or 0),
                        storage_gb=int(item.get("disk", 0) or 0),
                        storage_type=str(item.get("storage_type", "unknown")).upper(),
                        hourly_cost=hourly_net,
                        monthly_cost=monthly_net,
                        currency=currency,
                        instance_family=self._instance_family(str(item.get("name", ""))),
                        network_performance=f"{item.get('cpu_type', 'shared')} / {item.get('architecture', 'unknown')}",
                        last_updated=datetime.utcnow(),
                    )
                )

        return instances
