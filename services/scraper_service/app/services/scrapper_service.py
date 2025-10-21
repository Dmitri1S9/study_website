import asyncio
import json
import aiofiles
from scraper_service.app.services.data_processor.DataCollector import DataCollector
from scraper_service.app.services.data_processor.redditFetcher import FetchRedditAsync

class Scrapper:
    def __init__(self, character_name):
        self.character_name = character_name

    async def run(self):
        async with FetchRedditAsync(character_name=self.character_name) as parser:
            bd: DataCollector = await parser.execute(
                character_name=self.character_name,
                limit_posts=10,
                limit_comments=100
            )
            bd.collect_data()
            bd.normalize()
            print(bd)
            await self._save_result_async(bd.results)

    async def _save_result_async(self, results: dict):
        # for debugging
        file_path = f"results_{self.character_name.replace(' ', '_').lower()}.json"
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(results, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    scraper = Scrapper("General Grievous")
    asyncio.run(scraper.run())
