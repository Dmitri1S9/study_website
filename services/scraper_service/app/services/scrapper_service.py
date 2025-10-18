import asyncio

from scraper_service.app.services.data_processor.DataCollector import DataCollector
from scraper_service.app.services.data_processor.redditFetcher import FetchRedditAsync

class Scrapper:
    def __init__(self, character_name):
        self.character_name = character_name

    async def run(self):
        async with FetchRedditAsync(character_name=self.character_name) as parser:
            bd: DataCollector = await parser.execute(
                character_name=self.character_name,
                limit_posts=3,
                limit_comments=100
            )
            bd.collect_data()
            bd.normalize()
            print(bd)


if __name__ == "__main__":
    scraper = Scrapper("General Grievous")
    asyncio.run(scraper.run())
