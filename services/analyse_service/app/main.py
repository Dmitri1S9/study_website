from typing import List
from uuid import uuid4
import logging

from celery import chain
from fastapi import FastAPI, HTTPException, Depends, Body, Header

from app.ml_client.ml_config import FEATURE_NAME
from app.tasks import analyse_character_task, get_characters_by_universe_task, predict_character_task

log = logging.getLogger(__name__)

async def verify_token(authorization: str = Header(None)):
    if not authorization:
        log.error("no authorization header")
        raise HTTPException(status_code=401, detail="☠️☠️☠️☠️☠️ Missing Authorization header")
    if authorization != "Bearer secret_token_123":
        log.error("invalid authorization header")
        raise HTTPException(status_code=403, detail="☠️☠️☠️☠️☠️ Invalid or expired token")
    return {"user": "test_user"}


app = FastAPI(title="Character Scraper API")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Scraper API is alive 🚀"}

@app.get("/get_character_by_name_and_universe")
async def get_character(character_name: str, universe_name: str, user=Depends(verify_token)):
    raise NotImplementedError

@app.get("/get_characters_by_universe")
async def get_characters_by_universe(universe: str, user=Depends(verify_token)):
    raise NotImplementedError

@app.post("/post_characters")
async def post_characters(characters_list: List[List[str]] = Body(...), user=Depends(verify_token)):
    request_id = uuid4().hex[:5]
    log.info(f"post_character request %s", request_id)

    for name, universe in characters_list:
        res = analyse_character_task.delay(name, universe)
        log.info(f"⏰⏰⏰⏰⏰ CHA IN QUEUE: {name}, {universe}, id_in_queue={res.id}")

    return {"status": "OK", "HTTP code": 200}

@app.post("/post_characters_by_universe")
async def post_characters_by_universe(universes_list: List[str], user=Depends(verify_token)):
    request_id = uuid4().hex[:5]
    log.info(f"post_characters_by_universe request %s", request_id)

    for universe in universes_list:
        res = get_characters_by_universe_task.delay(universe)
        log.info(f"⏰⏰⏰⏰⏰ UNI IN QUEUE: {universe}, id_in_queue={res.id}")

    return {"status": "OK", "HTTP code": 200}

@app.get("/get_feature_by_name")
def get_feature_by_name(name: str, user=Depends(verify_token)):
    raise NotImplementedError

@app.get("/get_feature_by_name_and_universe")
def get_feature_by_name_and_universe(name: str, universe: str,
                                     feature: str = "flag_serious_violent_crime",
                                     user=Depends(verify_token)):
    log.info("YOU SHALL DIE WITH HONOR")
    sig = chain(
        analyse_character_task.s(name, universe),
        predict_character_task.s(feature),
    )
    res = sig.apply_async()
    try:
        predicted = res.get(timeout=60, propagate=True)
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout while waiting for prediction")
    return {"status": "OK", "feature": feature, "predicted": predicted, "status code": 200}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

