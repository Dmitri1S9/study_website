from pathlib import Path
import asyncio
from fastapi import FastAPI, HTTPException, Depends
import json
from scraper_service.app.services.scrapper_service import Scrapper
from auth import verify_token

app = FastAPI(title="Character Scraper API")
@app.get("/")
async def root():
    return {"message": "Scraper API is alive 🚀"}
@app.get("/get_character")
async def get_character(character_name: str, debug:bool = False, user=Depends(verify_token)):
    if debug:
        await asyncio.sleep(3)  # for example of a class work
        return {"status": "ok", "data": get_test_character_data()}
    else:
        try:
            scrapper = Scrapper(character_name, amount_of_posts=5, amount_of_comments_pro_post=100)
            data = await scrapper.run()
            if data is None:
                raise ValueError("Data is None")
            return {"status": "ok", "data": data.results}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

def get_test_character_data():
    file_path = Path(__file__).resolve().parent / "services" / "results_general_grievous.json"
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scraper_service.app.main:app", host="0.0.0.0", port=8000, reload=True)