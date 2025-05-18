import json
from abc import ABC, abstractmethod

import aiofiles

import config


class JobSourceStrategy(ABC):

    @abstractmethod
    async def get_scrape_jobs(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass


class LocalJsonFile(JobSourceStrategy):

    def __init__(self):
        self._description = 'Load JSON jobs from text file'
        self.file_path = config.JOB_FILE_PATH

    async def get_scrape_jobs(self):
        jobs = []

        async with aiofiles.open(self.file_path, mode='r') as f:
            async for line in f:
                line = line.strip()

                if not line:
                    continue
                try:
                    job = json.loads(line)
                    jobs.append(job)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Invalid JSON line skipped: {line} ({e})")

        return jobs

    @property
    def description(self):
        return self._description


def get_strategy_from_env() -> JobSourceStrategy:
    JOB_SOURCE = config.JOB_SOURCE

    if JOB_SOURCE == "file":
        return LocalJsonFile()
    else:
        raise ValueError(f"Unsupported job source strategy: {JOB_SOURCE}")
