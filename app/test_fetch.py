import asyncio
import pandas as pd
from dotenv import load_dotenv
from app.providers.aws_provider import AWSProvider
from app.providers.hetzner_cloud_provider import HetznerCloudProvider

async def main():
    """
    A simple script to test fetching data from a provider
    and saving it to a CSV file.
    """
    print("Loading environment variables from .env file...")
    load_dotenv()
    
    print("Initializing providers...")
    providers = [
        AWSProvider(),
        HetznerCloudProvider(),
    ]

    all_instances = []

    for provider in providers:
        name = provider.get_name()
        print(f"Fetching data from {name}... (This may take a few minutes)")
        try:
            provider_instances = await provider.fetch_data()
            print(f"Fetched {len(provider_instances)} rows from {name}.")
            all_instances.extend(provider_instances)
        except Exception as e:
            print(f"Failed to fetch from {name}: {e}")

    if not all_instances:
        print("No instances were fetched from any provider.")
        return

    print(f"Total fetched rows: {len(all_instances)}")

    df = pd.DataFrame([row.model_dump() for row in all_instances])

    output_file = "data/vm_pricing.csv"
    df.to_csv(output_file, index=False)
    print(f"Data successfully saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())