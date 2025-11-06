# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Archangel.settings')
# import django
# django.setup()
import requests
from typing import Dict, Optional
from apps.main_app.config import FETCHER_URL
from apps.main_app.models import Character, Characteristics, Title
from django.db import transaction

def api_get_check():
    response = requests.get(FETCHER_URL)
    response.raise_for_status()
    return response.json()

def api_get_character(character_name: str, debug: bool = False):
    param = {"character_name": character_name, "debug": f"{debug}"}
    headers = {"Authorization": "Bearer secret_token_123"}
    response = requests.get(FETCHER_URL + "/get_character", params=param, headers=headers)
    response.raise_for_status()
    return response.json()

def db_create_character(character_name: str, characteristics: Dict, title_name: Optional[str] = None):
    with transaction.atomic():
        title, _ = Title.objects.get_or_create(title_name=title_name or "Unknown")
        char, _ = Character.objects.get_or_create(name=character_name, title=title)
        Characteristics.objects.update_or_create(
            character=char,
            defaults={"characteristics": characteristics},
        )

def fetcher_processor(character_name: str, title_name: str, debug: bool = False):
    try:
        data = api_get_character(character_name=character_name, debug=debug)
        db_create_character(character_name=character_name, title_name=title_name, characteristics=data)
    except Exception as e:
        print(e)
    finally:
        print(list(Character.objects.all().values()))


if __name__ == '__main__':
    fetcher_processor(character_name="Reze", debug=True)
