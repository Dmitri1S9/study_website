import asyncio
import json
import aiofiles
from services.data_processor.DataCollector import DataCollector
from services.data_processor.redditFetcher import FetchRedditAsync

class Scrapper:
    def __init__(self, character_name, amount_of_posts: int = 30,
                 amount_of_comments_pro_post: int = 100):
        self.character_name = character_name
        self.amount_of_posts = amount_of_posts
        self.amount_of_comments_pro_post = amount_of_comments_pro_post

    async def run(self) -> DataCollector:
        async with FetchRedditAsync(character_name=self.character_name) as parser:
            bd: DataCollector = await parser.execute(
                character_name=self.character_name,
                limit_posts=self.amount_of_posts,
                limit_comments=self.amount_of_comments_pro_post
            )
            bd.collect_data()
            print("Collected data")
            bd.normalize()
            print("Normalized data")
            # await self._save_result_async(bd.results)
            return bd

    async def _save_result_async(self, results: dict):
        # for debugging
        file_path = f"results_{self.character_name.replace(' ', '_').lower()}.json"
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(results, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    scraper = Scrapper("Reze", 30, 100)
    print(asyncio.run(scraper.run()))
