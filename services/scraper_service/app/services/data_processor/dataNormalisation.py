import asyncio
from typing import List
from DataCollector import DataCollector
from scraper_service.app.services.redditFetcher import FetchRedditAsync
from scraper_service.app.services.db import Database

class DataNormalisation(DataCollector):
    def __init__(self, database: Database):
        super().__init__(database)

    def __enter__(self):
        self._create_result_database()
        self._process_text()
        self._collect_data()
        self._normalize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...


    def _normalize(self) -> None:
        """
        normalize characteristics
        """
        self._results["attitude"] = self.average_find(self._results["attitude"], 0.8),
        self._results["character"] = {i : str(self.average_find(self._results["character"][i])) + "%" for i in self._results["character"]}

    @staticmethod
    def average_find(l: List, k: float = 0.95) -> int:
        a, b = l
        a *= k  # cause there are more positive comments
        max_v = abs(a) + abs(b) + 1
        return round((a / max_v) * 100)

async def reddit_parser(character_name: str) -> Database:
    async with FetchRedditAsync(debug=True) as parser:
        return await parser.execute(character_name, limit_posts=3, limit_comments=100)


if __name__ == "__main__":
    db = asyncio.run(reddit_parser("General Grievous"))
    with DataNormalisation(db) as ana:
        print(ana)
