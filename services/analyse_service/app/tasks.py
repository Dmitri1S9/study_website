from openai import RateLimitError

from app.celery_app import celery
from app.clientOpenAI import OpenaiClient
import logging

from app.db import DBGet
from app.ml_client.ml_entities import Character
from app.ml_client.ml_prediction import MLPrediction
from app.serviceExceptions import CharacterException, OpenAIException

log = logging.getLogger(__name__)

@celery.task(bind=True, autoretry_for=(OpenAIException, RateLimitError),
             retry_backoff=True, retry_jitter=True, retry_kwargs={"max_retries": 3})
def analyse_character_task(self, character_name: str, universe_name: str) -> dict:
    return analyse_character(character_name, universe_name)


@celery.task(bind=True, autoretry_for=(OpenAIException, RateLimitError), retry_backoff=True, retry_jitter=True, retry_kwargs={"max_retries": 2})
def get_characters_by_universe_task(self, universe_name: str) -> dict:
    return get_characters_by_universe(universe_name)


@celery.task(bind=True,
             retry_backoff=True, retry_jitter=True, retry_kwargs={"max_retries": 2})
def predict_character_task(self, analyse_result: dict, feature: str = "flag_serious_violent_crime") -> dict:
    name = analyse_result["name"]
    universe = analyse_result["universe"]
    return predict_character(name, universe, feature)


def analyse_character(character_name: str, universe_name: str) -> dict:
    try:
        client = OpenaiClient()
        data = client.get_character_profile(character_name, universe_name)
        if data is None:
            return {"name": character_name, "universe": universe_name, "status": "🩵 ALREADY done"}
        client.save_character_to_db(character_name, universe_name, data)
    except CharacterException as e:
        log.exception("😡😡😡😡😡 Character not found, skipping")
        raise
    except RateLimitError as e:
        log.exception("😡😡😡😡😡 " + e.message)
        raise
    except OpenAIException as e:
        log.exception("😡😡😡😡😡 OpenAI Exception")
        raise
    except Exception:
        log.exception("😡😡😡😡😡 Unexpected error")
        raise
    return {"name": character_name, "universe": universe_name, "status": "💚 done"}


def get_characters_by_universe(universe_name: str) -> dict:
    try:
        client = OpenaiClient()
        data = client.get_universe_s_characters(universe_name)
        print(data)
        for character in data:
            print(character)
            analyse_character_task.delay(character, universe_name)

    except RateLimitError as e:
        log.exception("😡😡😡😡😡 " + e.message)
        raise
    except OpenAIException as e:
        log.exception("😡😡😡😡😡 OpenAI Exception")
        raise
    except Exception:
        log.exception("😡😡😡😡😡 Unexpected error")
        raise
    return {"universe": universe_name, "status": "💚 done"}


def predict_character(name: str, universe: str, feature: str = "flag_serious_violent_crime") -> dict:
    db_get = DBGet()
    character_id = int(db_get.get_character_id(name, universe)["id"])
    profile = db_get.get_character_profile(character_id)
    character = Character(profile=profile, character_id=0)

    orig = float(character.flat().get(feature, 0.0) or 0.0)
    all_v = MLPrediction.predict_from_profile(character, feature, "all")[1]
    app_v = MLPrediction.predict_from_profile(character, feature, "appearance")[1]
    prof_v = MLPrediction.predict_from_profile(character, feature, "profession")[1]
    psy_v = MLPrediction.predict_from_profile(character, feature, "psycho")[1]
    stat_v = MLPrediction.predict_from_profile(character, feature, "stat")[1]

    return { "data": (orig, all_v, app_v, prof_v, psy_v, stat_v) }