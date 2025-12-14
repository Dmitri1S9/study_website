import os
from pathlib import Path
import pytest
from dotenv import load_dotenv
from app.clientOpenAI import OpenaiClient

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

@pytest.mark.integration
def test_db():
    if os.getenv("DEBUG") is None:
        raise Exception("Please set DEBUG=True environment variable")

    character_name = "Suzune Horikita"
    universe_name = "Classroom of the Elite"

    client = OpenaiClient()
    data = client.get_character_profile(character_name, universe_name)
    client.save_character_to_db(character_name, universe_name, data)



