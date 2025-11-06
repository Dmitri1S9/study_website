import time

from celery import shared_task
from apps.main_app.clients.fetcher_client import fetcher_processor
from apps.main_app.config import RATE_LIMIT_SECONDS, COOLDOWN_ON_ERROR, MAX_RETRIES

def log_frame(text: str, symbol: str = "🔷", width: int = 6):
    border = symbol * width
    print(f"{border}{text.center(width)}{border}")

@shared_task
def queue_all_characters(json_path="/app/apps/main_app/characters.json", debug : bool = False):
    import json
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log_frame(f" json file not found: {json_path}", "❌")
        print(e)
        return

    errors_in_succession = 0
    all_errors = 0
    delta = 60
    for item in data:
        name = item.get("character")
        title = item.get("title") if item.get("title") else "idk"
        if not name:
            continue
        if errors_in_succession >= 3:
            log_frame("Reddit API kill us, watch logs your self", "💀")
            return

        try:
            log_frame(f" processing: {name}")
            fetcher_processor(name, title, debug)

            from django.db import connection
            connection.commit()
            connection.close()

        except Exception as e:
            log_frame(f"Exception {e}", "⚠️")
            errors_in_succession += 2
            all_errors += 1
            log_frame(f"sleeping for {COOLDOWN_ON_ERROR} seconds")
            time.sleep(COOLDOWN_ON_ERROR)
        else:
            errors_in_succession = 0
            log_frame(f"{name} is ready ")
            log_frame(f"sleeping for {RATE_LIMIT_SECONDS + delta * (all_errors // 3)} seconds")
            time.sleep(RATE_LIMIT_SECONDS)

