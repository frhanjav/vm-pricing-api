import asyncio
import pandas as pd
from dotenv import load_dotenv
from app.providers.aws_provider import AWSProvider

async def main():
    """
    A simple script to test fetching data from a provider
    and saving it to a CSV file.
    """
    print("Loading environment variables from .env file...")
    load_dotenv()
    
    print("Initializing AWS Provider...")
    aws_provider = AWSProvider()
    
    print("Fetching data from AWS... (This may take a few minutes)")
    try:
        instances = await aws_provider.fetch_data()
        
        if not instances:
            print("No instances were fetched. Please check your credentials and permissions.")
            return

        print(f"Successfully fetched {len(instances)} instance types from AWS.")
        
        # Convert to a pandas DataFrame
        df = pd.DataFrame([vars(d) for d in instances])
        
        # Save to a CSV file
        output_file = "data/vm_pricing.csv"
        df.to_csv(output_file, index=False)
        print(f"Data successfully saved to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("\nCommon issues to check:")
        print("1. Are your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY correct in the .env file?")
        print("2. Does your IAM user have 'pricing:GetProducts' permissions?")
        print("3. Is your internet connection working?")

if __name__ == "__main__":
    asyncio.run(main())