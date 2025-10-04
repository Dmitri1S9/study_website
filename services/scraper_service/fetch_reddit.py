import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import asyncpraw
import asyncio

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")


class FetchRedditAsync:
    def __init__(self, debug: bool = False) -> None:
        self.__reddit = None
        self.__pattern = self.__get_patterns()
        if debug:
            self.__clear_db()

    async def __init_reddit(self):
        if not self.__reddit:
            self.__reddit = asyncpraw.Reddit(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                user_agent=USER_AGENT
            )

    async def execute(self, character_name: str) -> None:
        await self.__init_reddit()
        posts = await self.__fetch_posts(character_name)
        for post_id in posts:
            await self.__fetch_post_with_comments(post_id)

        print(posts)

        for post in posts:
            print(post)
            entry = await self.__fetch_post_with_comments(post)
            if entry:
                self.__save_to_db(character_name, entry)
        print(f"Finished fetching data for {character_name}")

    @staticmethod
    def __clear_db() -> None:
        # clean json file before starting
        db_path = BASE_DIR / "scraper_service/db.json"
        if db_path.exists():
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump({}, f)
        else:
            raise FileNotFoundError(f"File {db_path} not found")

    @staticmethod
    def __save_to_db(character_name:str, entry:dict) -> None:
        db_path = BASE_DIR / "scraper_service/db.json"
        if db_path.exists():
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            if character_name not in db:
                db[character_name] = []
            db[character_name].append(entry)
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=4)
        else:
            raise FileNotFoundError(f"File {db_path} not found")

    @staticmethod
    def __get_patterns():
        with open(BASE_DIR / "scraper_service/patterns.json", "r", encoding="utf-8") as f:
            return json.load(f)

    async def __fetch_posts(self, post_title:str, limit:int=10) -> set:
        """
        fetch post's ids with name 'post_title + key word' from reddit
        """
        subreddit = await self.__reddit.subreddit("all")
        post_ids = set()
        async for submission in subreddit.search(post_title, sort="relevance", limit=limit):
            post_ids.add(submission.id)
        return post_ids


    async def __fetch_post_with_comments(self, post_id:str|None, limit:int=100) -> dict[str, list]|None:
        """
        :param post_id: id of the post to fetch comments from
        :param limit: limit of comments to fetch per post
        :return: None
        """
        post = await self.__reddit.submission(id=post_id)
        if post.score < 100:
            return None
        entry = {
            "ID": post.id,
            "text": post.selftext,
            "score": post.score,
            "post_created": post.created_utc,
            "comments": []
        }

        await post.comments.replace_more(limit=limit)
        comments = []
        for comment in post.comments.list():
            if comment.score > 4:
                comments.append({
                    "text": comment.body,
                    "score": comment.score,
                    "comment_created": comment.created_utc
                })
        entry["comments"] = comments
        return entry



if __name__ == "__main__":
    parser = FetchRedditAsync(debug=True)
    asyncio.run(parser.execute("General Grievous"))