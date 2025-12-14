from typing import List
from uuid import uuid4
from app.clientOpenAI import OpenaiClient
from app.logger_setup import setup_logging
import logging
from fastapi import FastAPI, HTTPException, Depends, Body, Header
from app.servisExceptions import CharacterException, OpenAIException


setup_logging()
log = logging.getLogger(__name__)


async def verify_token(authorization: str = Header(None)):
    if not authorization:
        log.error("no authorization header")
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if authorization != "Bearer secret_token_123":
        log.error("invalid authorization header")
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    return {"user": "test_user"}


app = FastAPI(title="Character Scraper API")
@app.get("/")
async def root():
    return {"status": "ok", "message": "Scraper API is alive 🚀"}

@app.get("/get_character_by_name_and_universe")
async def get_character(character_name: str, universe_name: str, user=Depends(verify_token)):
    ...

@app.get("/get_characters_by_universe")
async def get_characters_by_universe(universe: str, user=Depends(verify_token)):
    ...

@app.get("/get_character_by_name")
async def get_character(name: str, user=Depends(verify_token)):
    ...

@app.post("/post_characters")
async def post_characters(characters_list: List[List[str]] = Body(...), user=Depends(verify_token)):
    request_id = uuid4().hex[:5]
    log.info(f"post_character request %s", request_id)
    for name, universe in characters_list:
        log.info(f"analyse of character with name {name}, universe {universe}")
        analyse_new_character(name, universe)
    log.info("the end of analyse of request %s", request_id)
    return {"status": "OK", "HTTP code": 200}

def analyse_new_character(character_name: str, universe_name: str):
    try:
        client = OpenaiClient()
        data = client.get_character_profile(character_name, universe_name)
        client.save_character_to_db(character_name, universe_name, data)
    except CharacterException as e:
        log.exception("Character not found, skipping")
        raise
    except OpenAIException as e:
        log.exception("OpenAI Exception")
        raise
    except Exception:
        log.exception("Unexpected error")
        raise


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

