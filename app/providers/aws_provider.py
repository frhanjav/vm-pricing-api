import boto3
import json
from typing import List, Dict, Any
from datetime import datetime
from app.api.schemas import VMInstance
from .base_provider import BaseProvider
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

class AWSProvider(BaseProvider):
    def __init__(self):
        super().__init__("AWS")
        
        # boto3 will automatically look for credentials in this order:
        # 1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        # 2. The ~/.aws/credentials file
        # This setup prioritizes your .env file thanks to load_dotenv()
        self.pricing_client = boto3.client(
            "pricing", 
            region_name="us-east-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

    async def fetch_data(self) -> List[VMInstance]:
        """
        Fetches EC2 pricing data using the AWS Pricing API.
        This is a simplified example focusing on On-Demand Linux instances.
        """
        instances = []
        paginator = self.pricing_client.get_paginator("get_products")
        pages = paginator.paginate(
            ServiceCode="AmazonEC2",
            Filters=[
                {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
                {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
                {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
                {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
            ],
        )

        for page in pages:
            for product_json in page["PriceList"]:
                product = json.loads(product_json)
                
                # OnDemand pricing details
                on_demand_terms = product.get("terms", {}).get("OnDemand")
                if not on_demand_terms:
                    continue

                sku = list(on_demand_terms.keys())[0]
                price_dimensions = list(on_demand_terms[sku]["priceDimensions"].values())
                if not price_dimensions:
                    continue
                
                price_per_hour_str = price_dimensions[0].get("pricePerUnit", {}).get("USD")
                if not price_per_hour_str or float(price_per_hour_str) == 0.0:
                    continue

                attrs = product["product"]["attributes"]
                
                try:
                    instance = VMInstance(
                        instance_name=attrs.get("instanceType"),
                        provider=self.provider_name,
                        region=attrs.get("location"),
                        vcpus=int(attrs.get("vcpu")),
                        memory_gb=float(str(attrs.get("memory")).replace(" GiB", "")),
                        storage_gb=int(str(attrs.get("storage", "0 GB")).split(" ")[0].replace(",", "")) if "EBS" not in attrs.get("storage", "") else 0,
                        storage_type=attrs.get("storage", "EBS Only"),
                        hourly_cost=float(price_per_hour_str),
                        monthly_cost=float(price_per_hour_str) * 730,
                        instance_family=attrs.get("instanceFamily"),
                        network_performance=attrs.get("networkPerformance"),
                        last_updated=datetime.utcnow()
                    )
                    instances.append(instance)
                except (ValueError, TypeError) as e:
                    # Skip if data is malformed
                    continue
        
        return instances