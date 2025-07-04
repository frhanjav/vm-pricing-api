import pandas as pd
import aiofiles
import asyncio
from typing import List, Optional
from app.api.schemas import VMInstance
from app.core.config import settings
import os
from datetime import datetime
from io import StringIO

class DataManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df: Optional[pd.DataFrame] = None
        self._lock = asyncio.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            # Create empty file with headers
            pd.DataFrame(columns=[f.name for f in VMInstance.__fields__.values()]).to_csv(self.file_path, index=False)

    async def load_data(self):
        async with self._lock:
            try:
                # Use aiofiles to read the file asynchronously. [2]
                async with aiofiles.open(self.file_path, mode='r', encoding='utf-8') as f:
                    content = await f.read()
                from io import StringIO
                self.df = pd.read_csv(StringIO(content))
                # Convert date columns
                self.df['last_updated'] = pd.to_datetime(self.df['last_updated'])
            except (FileNotFoundError, pd.errors.EmptyDataError):
                self.df = pd.DataFrame(columns=[f.name for f in VMInstance.__fields__.values()])

    async def update_provider_data(self, provider: str, new_data: List[VMInstance]):
        if not new_data:
            return

        new_df = pd.DataFrame([vars(d) for d in new_data])
        
        async with self._lock:
            if self.df is None:
                await self.load_data()

            # Remove old data for the provider
            self.df = self.df[self.df['provider'] != provider]
            
            # Add new data
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            
            # Persist to CSV asynchronously
            buffer = StringIO()
            self.df.to_csv(buffer, index=False)
            buffer.seek(0)
            async with aiofiles.open(self.file_path, mode='w', encoding='utf-8') as f:
                await f.write(buffer.getvalue())

    def get_all_instances(self) -> pd.DataFrame:
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        return self.df

    def get_last_update_times(self) -> dict:
        if self.df is None or self.df.empty:
            return {p: None for p in settings.SUPPORTED_PROVIDERS}
        
        last_updates = self.df.groupby('provider')['last_updated'].max().to_dict()
        # Ensure all supported providers are in the dictionary
        for p in settings.SUPPORTED_PROVIDERS:
            if p not in last_updates:
                last_updates[p] = None
        return last_updates


data_manager = DataManager(settings.DATA_FILE_PATH)