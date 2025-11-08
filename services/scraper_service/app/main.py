from pathlib import Path
import asyncio
from fastapi import FastAPI, HTTPException, Depends
import json
from services.scrapper_service import Scrapper
from auth import verify_token

app = FastAPI(title="Character Scraper API")
@app.get("/")
async def root():
    return {"status": "ok", "message": "Scraper API is alive 🚀"}

@app.get("/get_character")
async def get_character(character_name: str, debug: bool = False, user=Depends(verify_token)):
    try:
        if debug:
            return {"status": "ok", "data": get_test_character_data()}

        scrapper = Scrapper(character_name, amount_of_posts=30, amount_of_comments_pro_post=100)
        data = await scrapper.run()

        if not data:
            print("[WARN] Scrapper returned None or empty data")
            return {"status": "error", "data": "scrapper returned empty result"}

        results = getattr(data, "results", None)
        if not results:
            print("[WARN] No results attribute or it's empty")
            return {"status": "error", "data": "no results found in scrapper output"}

        print(f"[INFO] Successfully fetched {len(results)} results for {character_name}")
        return {"status": "ok", "data": results}

    except Exception as e:
        print(f"[ERROR] Failed to fetch character '{character_name}': {e}")
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


def get_test_character_data():
    file_path = Path(__file__).resolve().parent / "services" / "results_reze.json"
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scraper_service.app.main:app", host="0.0.0.0", port=8000, reload=True)