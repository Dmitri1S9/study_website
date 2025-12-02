import math
import os
import json
import random
from pathlib import Path
from dotenv import load_dotenv
import asyncpraw
import asyncio
from typing import Any, Dict, List, Set, Optional

from services.data_processor.DataCollector import DataCollector
# from app.services.data_processor.DataCollector import DataCollector
from services.data_processor.bd import BaseDB
# from app.services.data_processor.bd import BaseDB

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent.parent / ".env")

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")

NEGATIONS = {"not", "no", "never", "n't"}
REINFORCEMENT = {"very"}


class FetchRedditAsync:
    @staticmethod
    def _get_patterns() -> List[str]:
        with open(BASE_DIR / "data" / "patterns.json", "r", encoding="utf-8") as f:
            return json.load(f)["core_patterns"]

    def __init__(self, character_name: str) -> None:
        self.db = DataCollector(character_name)
        self.postgres = BaseDB()
        self.character_name = character_name
        self._reddit: Optional[asyncpraw.Reddit] = None
        self._pattern: List[str] = self._get_patterns()
        self.character_texts = self.postgres.get_character(self.character_name)
        self.character_ids = self.postgres.get_character_ids(self.character_name)

    async def __aenter__(self):
        if len(self.character_texts) < 500:
            await self._init_reddit()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._reddit:
            await self._reddit.close()

    async def execute(self, character_name: str, limit_posts:int=10, limit_comments:int=1000) -> DataCollector:
        for pattern in self._pattern:
            await self._execute_with_query(
                (character_name + " " + pattern).strip(),
                limit_posts=limit_posts,
                limit_comments=limit_comments
            )
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
                                  limit_comments: int = 1000
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
        i = 0
        if len(self.character_texts) < 500:
            posts = await self._fetch_posts(query, limit_posts)
            print("New posts are fetched and now would be processed")
            for post_id in posts:
                i += 1
                await self._fetch_post_with_comments(post_id[0], limit_comments, post_id[1])
                if i % 10 == 0:
                    await asyncio.sleep(5)
            print("posts are fetched and now would be processed")
        else:
            print("Old posts would be processed")
            for text in self.character_texts:
                self._count_words(
                    text=self.db.textProcessor.clean_text(text[-2], self.db.ignore_words),
                    score=text[-3]
                )

    async def _fetch_posts(self, post_title: str, limit: int = 10) -> Set[tuple]:
        """
        Fetch post IDs with name 'post_title + keyword' from Reddit
        """
        subreddit = await self._reddit.subreddit("all")
        post_ids: Set = set()

        i = 0
        async for submission in subreddit.search(post_title, sort="relevance", limit=limit // 3 + 1):
            i += 1
            if (
                    any(word in submission.title.lower() for word in self.character_name.lower().split()) and
                    submission.id not in self.character_ids
            ):
                post_ids.add((submission.id, 1))
            if i % 10 == 0:
                await asyncio.sleep(random.uniform(1, 3))

        i = 0
        async for submission in subreddit.search(post_title, sort="top", limit=limit // 3 + 1):
            i += 1
            if (
                    any(word in submission.title.lower() for word in self.character_name.lower().split()) and
                    submission.id not in self.character_ids
            ):
                post_ids.add((submission.id, 1))
            if i % 10 == 0:
                await asyncio.sleep(random.uniform(1, 3))

        i = 0
        async for submission in subreddit.search(post_title, sort="most_comment", limit=limit // 3 + 1):
            i += 1
            if (
                    submission.num_comments > 3 and
                    submission.id not in self.character_ids
            ):
                post_ids.add((submission.id, 0.3))
            if i % 10 == 0:
                await asyncio.sleep(random.uniform(1, 3))

        return post_ids

    async def _fetch_post_with_comments(self, post_id: Optional[str], limit: int = 100, k: int = 1) -> Optional[Dict[str, Any]]:
        """
        :param post_id: id of the post to fetch comments from
        :param limit: limit of comments to fetch per post
        :return: None
        """
        content_to_db = []
        post = await self._reddit.submission(id=post_id)
        for sentence in post.title.split("."):
            self._count_words(
                text=self.db.textProcessor.clean_text(sentence, self.db.ignore_words),
                score=post.score,
                k_=k
            )
            content_to_db.append((post.id, self.character_name, round(post.score * k), sentence))

        await post.comments.replace_more(limit=limit)
        comments = post.comments.list()
        i = 0
        for comment in comments:
            i += 1
            if comment.score >= 0:
                for sentence in comment.body.split("."):
                    self._count_words(
                        text=self.db.textProcessor.clean_text(sentence, self.db.ignore_words),
                        score=comment.score,
                        k_=k
                    )
                    content_to_db.append((comment.id, self.character_name, round(comment.score * k), sentence))
            if i % 50 == 0:
                await asyncio.sleep(random.uniform(0.50, 1.02))
        self.postgres.insert_many(content_to_db)

    def _count_words(self, text: List[str], score: int, k_: int = 1) -> None:
        k = k_ * 2 if any(word in text for word in self.character_name.lower().split()) else k_
        base_direct = round(word_boost(score) * k + 1)
        base_related = round(word_boost(score + 1) * 0.5 * k)

        for idx, word in enumerate(text):
            negated = 1
            very = 1
            left = max(0, idx - 4)
            right = min(len(text), idx + 1)
            window_forward = text[left:right]
            if any(n in window_forward for n in NEGATIONS):
                negated = -0.9
            if any(r in window_forward for r in REINFORCEMENT):
                very = 1.5

            if word in self.db.words:
                self.db.words_counter[word] += negated * base_direct
            elif idx >= 1 and text[idx - 1] + " " + text[idx] in self.db.words:
                self.db.words_counter[text[idx - 1] + " " + text[idx]] += negated * very * base_related * 2
            else:
                self.db.new_words_counter[word] += negated * very * base_direct * 2


def word_boost(n: float) -> int:
    return round(math.log2(n + 1)) + 1

if __name__ == "__main__":
    ...