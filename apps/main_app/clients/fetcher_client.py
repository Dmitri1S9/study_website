import requests
from apps.main_app.config import FETCHER_URL

class FetcherClient:
    def __init__(self):
        pass

def check_fetcher():
    response = requests.get(FETCHER_URL)
    response.raise_for_status()
    return response.json()

def get_character(name: str, debug: bool = False):
    param = {"character_name": name, "debug":f"{debug}"}
    headers = {"Authorization": "Bearer secret_token_123"}
    response = requests.get(FETCHER_URL+"/get_character", params=param, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    print(check_fetcher())
    print(get_character("Reze", debug=False))