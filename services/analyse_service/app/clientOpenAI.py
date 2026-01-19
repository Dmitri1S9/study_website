import logging
from typing import Dict, Any, List
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os
import json
from app.db import DBPost, DBGet
from app.serviceExceptions import *

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class OpenaiClient:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.getenv("API_KEY"))
        self.log = logging.getLogger(__name__)
        self.debug = os.getenv("DEBUG").strip().lower() == "true"
        self.db_post = DBPost()
        self.db_get = DBGet()

    def get_character_profile(self, name: str, universe: str) -> dict | None:
        def check_data(output_data: Dict[str, Any]) -> Dict[str, Any]:
            if output_data["name"] == -1 or output_data["universe"] == -1:
                #we need to retry
                raise CharacterException
            if output_data is None:
                # we need a timeout
                raise OpenAIException
            return output_data

        if self.debug:
            self.log.info("DEBUG")
            return json.load(open(BASE_DIR / "app/data/test_response.json", "r"))

        if self.db_get.get_character_id(name, universe):
            self.log.info("already exists")
            return None

        resp = self.client.responses.create(
            prompt={
                "id": os.getenv("PROMPT_ID"),
                "version": os.getenv("PROMPT_VERSION"),
                "variables": {
                    "character_name": name,
                    "universe_name": universe,
                },
            },
            input=[{"role": "system", "content": "json"}],
            text={"format": {"type": "json_object"}},
        )
        # service_tier="flex",
        self.log.info(f"🍏🍏🍏🍏🍏 character {name} from {universe} was got from OpenAI")
        data = json.loads(resp.output_text)
        return check_data(data)

    def check_characters_list(self, universe: str, character_list: List[str]) -> dict | None:
        resp = self.client.responses.create(
            prompt={
                "id": os.getenv("CHECK_PROMPT_ID"),
                "version": os.getenv("CHECK_PROMPT_VERSION"),
                "variables": {
                    "universe_name": universe,
                    "candidates_json_array": json.dumps(character_list, ensure_ascii=False),
                },
            },
            input=[{"role": "system", "content": "json"}],
            text={"format": {"type": "json_object"}},
            service_tier="flex",
        )
        self.log.info(f"🌳🌳🌳🌳🌳{universe} was checked by OpenAI")
        data = json.loads(resp.output_text)
        return data

    def get_universe_s_characters(self, universe: str) -> dict | None:
        def check_data(output_data: Dict[str, Any]) -> Dict[str, Any]:
            if not output_data["characters"]:
                raise EmptyUniverseException
            if output_data is None:
                raise OpenAIException
            return output_data

        resp = self.client.responses.create(
            prompt={
                "id": os.getenv("GCBU_PROMPT_ID"),
                "version": os.getenv("GCBU_PROMPT_VERSION"),
                "variables": {
                    "universe_name": universe,
                },
            },
            input=[{"role": "system", "content": "json"}],
            text={"format": {"type": "json_object"}},
        )
        self.log.info(f"🌳🌳🌳🌳🌳{universe} was got from OpenAI")
        data = json.loads(resp.output_text)
        # return check_data(data)["characters"]
        return check_data(self.check_characters_list(universe, data["characters"]))["characters"]

    def save_character_to_db(self, character_name, universe, character_profile: Dict[str, Any]) -> None:
        if self.debug:
            self.log.info("DEBUG")
            self.db_post.test_connection()
            character_name = "test_name"
            universe = "test_universe"

        with self.db_post as db:
            universe_id = db.addition_table_universes(universe_name=universe),
            db.addition_table_entries(
                db.addition_table_characters(character_name=character_name, universe_id=universe_id),
                db.addition_table_profiles(profile=character_profile)
            )
            self.log.info(f"👽👽👽👽👽 character {character_name} from {universe} was saved to database")

    # @staticmethod
    # def build_batch_line(
    #         character_name: str,
    #         universe_name: str,
    # ) -> str:
    #     user_content = f'character_name = "{character_name}"\nuniverse_name  = "{universe_name}"'
    #     from app.data.prompt import SYSTEM_PROMPT
    #     json_content = {
    #         "custom_id": character_name + "_" + universe_name,
    #         "method": "POST",
    #         "url": "/v1/chat/completions",
    #         "body": {
    #             "model": "gpt-5-nano",
    #             "messages": [
    #                 {"role": "system", "content": SYSTEM_PROMPT},
    #                 {"role": "user", "content": user_content},
    #             ],
    #             "response_format": {"type": "json_object"},
    #             "reasoning_effort": "medium",
    #             "verbosity": "low",
    #             "store": True,
    #         },
    #     }
    #     with open(f"data/{character_name} + _ + {universe_name}.jsonl", "w", encoding="utf-8") as f:
    #         f.write(json_content)
    #     return f"data/{character_name} + _ + {universe_name}.jsonl"
    #
    # def get_character_profile_batch(self) -> str:
    #     with open("app/data/batch.jsonl", "rb") as f:
    #         batch_input_file = self.client.files.create(
    #             file=f,
    #             purpose="batch",
    #         )
    #     batch = self.client.batches.create(
    #         input_file_id=batch_input_file.id,
    #         endpoint="/v1/chat/completions",
    #         completion_window="24h",
    #     )
    #     self.log.info(f"Batch created: {batch.id} status={batch.status}")


if __name__ == "__main__":
    ...


