import logging
from typing import Dict, Any
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os
import json
from app.bd import DBWorker
from app.servisExceptions import *

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class OpenaiClient:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.getenv("API_KEY"))
        self.log = logging.getLogger(__name__)
        self.debug = os.getenv("DEBUG")
        self.db = DBWorker()

    def get_character_profile(self, name: str, universe: str) -> dict:
        def check_data(data: Dict[str, Any]) -> Dict[str, Any]:
            if data["name"] == -1 | data["universe"] == -1:
                raise CharacterException
            if data is None:
                raise OpenAIException
            return data

        if self.debug:
            self.log.debug("Getting character profile from OpenAI")
            return json.load(open("data/test_response.json", "r"))

        resp = self.client.responses.create(
            prompt={
                "id": os.getenv("PROMPT_ID"),
                "version": os.getenv("PROMPT_VERSION"),
                "variables": {
                    "character_name": name,
                    "universe_name": universe,
                },
            },
            input=[],
            max_output_tokens=2000
        )
        self.log.info(f"character {name} from {universe} was got from OpenAI")
        return check_data(resp.output_text)

    def save_character_to_db(self, character_name, universe, character_profile: Dict[str, Any]) -> None:
        if self.debug:
            self.db.test_connection()
            character_name = "test_name"
            universe = "test_universe"

        with self.db as db:
            db.update_table_entries(
                db.update_table_characters(character_name=character_name),
                db.update_table_universes(universe_name=universe),
                db.update_table_profiles(profile=character_profile)
            )
            self.log.info(f"character {character_name} from {universe} was saved to database")


if __name__ == "__main__":
    ...


