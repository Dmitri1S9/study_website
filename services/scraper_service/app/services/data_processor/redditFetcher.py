import math
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import asyncpraw
import asyncio
from typing import Any, Dict, List, Set, Optional

from scraper_service.app.services.data_processor.DataCollector import DataCollector
from scraper_service.app.services.data_processor.wordAnalyser import get_related_words

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent.parent / ".env")

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")


class FetchRedditAsync:
    @staticmethod
    def _get_patterns() -> List[str]:
        with open(BASE_DIR / "data" / "patterns.json", "r", encoding="utf-8") as f:
            return json.load(f)["core_patterns"]

    def __init__(self, character_name: str) -> None:
        self.db = DataCollector(character_name)
        self.character_name = character_name
        self._reddit: Optional[asyncpraw.Reddit] = None
        self._pattern: List[str] = self._get_patterns()

    async def __aenter__(self):
        await self._init_reddit()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._reddit:
            await self._reddit.close()

    async def execute(self, character_name: str, limit_posts:int=10, limit_comments:int=100) -> DataCollector:
        for pattern in self._pattern:
            await self._execute_with_query(
                (character_name + " " + pattern).strip(),
                limit_posts=limit_posts,
                limit_comments=limit_comments
            )
            await asyncio.sleep(limit_posts + 1) # to avoid rate limit
        return self.db

    async def _init_reddit(self) -> None:
        if not self._reddit:
            self._reddit = asyncpraw.Reddit(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                user_agent=USER_AGENT
            )

    async def _execute_with_query(self,
                                  query: str,
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
        posts = await self._fetch_posts(query, limit_posts)
        for post_id in posts:
            await self._fetch_post_with_comments(post_id, limit_comments)

    async def _fetch_posts(self, post_title: str, limit: int = 10) -> Set[str]:
        """
        Fetch post IDs with name 'post_title + keyword' from Reddit
        """
        subreddit = await self._reddit.subreddit("all")
        post_ids: Set[str] = set()
        async for submission in subreddit.search(post_title, sort="comments", limit=limit):
            if (
                    submission.num_comments > 20 and
                    any(word in submission.title.lower() for word in self.character_name.lower().split())
            ):
                post_ids.add(submission.id)

        return post_ids

    async def _fetch_post_with_comments(self, post_id: Optional[str], limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        :param post_id: id of the post to fetch comments from
        :param limit: limit of comments to fetch per post
        :return: None
        """
        post = await self._reddit.submission(id=post_id)
        self._count_words(
            text=self.db.textProcessor.clean_text(post.title, self.db.ignore_words),
            score=post.score
        )

        await post.comments.replace_more(limit=limit)
        for comment in post.comments.list():
            if comment.score > 1:
                self._count_words(
                    text=self.db.textProcessor.clean_text(comment.body, self.db.ignore_words),
                    score=comment.score
                )

    def _count_words(self, text: List[str], score: int) -> None:
        k = 2 if any(word in text for word in self.character_name.lower().split()) else 1
        for word in text:
            if word in self.db.words:
                self.db.words_counter[word] += round(math.log(score * k))
            elif self._word_in_characters(word):
                related_words = get_related_words(word)
                for i in related_words:
                    if i in self.db.words and i not in self.db.ignore_words:
                        self.db.words_counter[i] += round(math.log(score) * 0.5 * k)
                        self.db.words.add(i)
            else:
                self.db.ignore_words.add(word)

    def _word_in_characters(self, word: str) -> bool:
        if self.db.get_path.get(word) is None:
            return False
        for path in self.db.get_path[word]:
            if "character" in path:
                return True
        else:
            return False


if __name__ == "__main__":
    ...