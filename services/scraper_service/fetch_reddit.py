import os
import json
from pathlib import Path
from dotenv import load_dotenv
import asyncpraw
import asyncio
from typing import Any, Dict, List, Set, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")


class FetchRedditAsync:
    @staticmethod
    def __get_patterns() -> List[str]:
        with open(BASE_DIR / "scraper_service/patterns.json", "r", encoding="utf-8") as f:
            return json.load(f)["core_patterns"]

    @staticmethod
    def __clear_db() -> None:
        db_path = BASE_DIR / "scraper_service/db.json"
        if db_path.exists():
            with open(db_path, "w", encoding="utf-8") as _:
                json.dump({}, _, ensure_ascii=False, indent=2)
        else:
            raise FileNotFoundError(f"File {db_path} not found")

    @staticmethod
    def __save_to_db(character_name: str, entry: Dict[str, Any]) -> None:
        db_path = BASE_DIR / "scraper_service/db.json"
        if db_path.exists():
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            if character_name not in db:
                db[character_name] = []
            db[character_name].append(entry)
            with open(db_path, "w", encoding="utf-8") as _:
                json.dump(db, _, ensure_ascii=False, indent=4)
        else:
            raise FileNotFoundError(f"File {db_path} not found")

    def __init__(self, debug: bool = False) -> None:
        self.__reddit: Optional[asyncpraw.Reddit] = None
        self.__pattern: List[str] = self.__get_patterns()
        if debug:
            self.__clear_db()

    async def __aenter__(self):
        await self.__init_reddit()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.__reddit:
            await self.__reddit.close()

    async def execute(self, character_names: str, limit_posts:int=10, limit_comments:int=100) -> None:
        for pattern in self.__pattern:
            await self.__execute_with_query(
                (character_names + " " + pattern).strip(),
                limit_posts=limit_posts,
                limit_comments=limit_comments
            )

    async def __init_reddit(self) -> None:
        if not self.__reddit:
            self.__reddit = asyncpraw.Reddit(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                user_agent=USER_AGENT
            )

    async def __execute_with_query(self, query: str,
                                   limit_posts: int = 10,
                                   limit_comments: int = 100
                                   ) -> None:
        """
        1. Fetch posts with title 'query' from Reddit
        2. For each post, fetch comments
        3. Save post and comments to db

        :param query: character name + pattern
        :param limit_posts: default is 10
        :param limit_comments: default is 100
        :return: None
        """
        posts = await self.__fetch_posts(query, limit_posts)
        for post_id in posts:
            entry = await self.__fetch_post_with_comments(post_id, limit_comments)
            if entry:
                self.__save_to_db(query, entry)
                await asyncio.sleep(1) # to avoid rate limit

    async def __fetch_posts(self, post_title: str, limit: int = 10) -> Set[str]:
        """
        Fetch post IDs with name 'post_title + keyword' from Reddit
        """
        subreddit = await self.__reddit.subreddit("all")
        post_ids: Set[str] = set()
        async for submission in subreddit.search(post_title, sort="relevance", limit=limit):
            if submission.score > 100:
                post_ids.add(submission.id)
        return post_ids

    async def __fetch_post_with_comments(self, post_id: Optional[str], limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        :param post_id: id of the post to fetch comments from
        :param limit: limit of comments to fetch per post
        :return: None
        """
        post = await self.__reddit.submission(id=post_id)
        if post.score < 100:
            return None
        entry: Dict[str, Any] = {
            "ID": post.id,
            "text": post.selftext,
            "title": post.title,
            "score": post.score,
            "post_created": post.created_utc,
            "comments": []
        }

        await post.comments.replace_more(limit=limit)
        comments: List[Dict[str, Any]] = []
        for comment in post.comments.list():
            if comment.score > 4:
                comments.append({
                    "text": comment.body,
                    "score": comment.score,
                    "comment_created": comment.created_utc
                })
        entry["comments"] = comments
        return entry


async def reddit_parser(character_name: str) -> None:
    async with FetchRedditAsync(debug=True) as parser:
        await parser.execute(character_name, limit_posts=20, limit_comments=100)


if __name__ == "__main__":
    asyncio.run(reddit_parser("General Grievous"))
