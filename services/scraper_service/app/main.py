from pathlib import Path
from typing import Union, Any, Coroutine
import asyncio
from fastapi import FastAPI, HTTPException
import json
from scraper_service.app.services.scrapper_service import Scrapper

app = FastAPI()


@app.get("/get_character")
async def get_character() -> None:
    await asyncio.sleep(3)  # for example of a class work


def get_test_character_data():
    file_path = Path(__file__).resolve().parent / "services" / "results_general_grievous.json"
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    print(get_test_character_data())
