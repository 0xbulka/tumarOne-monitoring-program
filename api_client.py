import os
import requests
from config import LANG, TUMAR_API_URL, MOCK_URL

USE_MOCK = os.getenv("USE_MOCK", "0") == "1"

def fetch_programs(access_token: str | None = None):
    if USE_MOCK:
        return _fetch_mock()
    return _fetch_real(access_token)

def _fetch_real(access_token: str):
    """
    Fetches the list of programs using the given access_token
    and returns list of program dicts. Raises on error.
    """
    payload = {
        "operationName": "GetPrograms",
        "query": (
            "query GetPrograms($lang: Language) {\n"
            "  viewer {\n"
            "    projects {\n"
            "      list(lang: $lang) {\n"
            "        id\n"
            "        name\n"
            "        logo\n"
            "        shortDescription\n"
            "        private\n"
            "        reports { count }\n"
            "        contacts\n"
            "        created\n"
            "      }\n"
            "    }\n"
            "  }\n"
            "}"
        ),
        "variables": {"lang": LANG},
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    response = requests.post(TUMAR_API_URL, json=payload, headers=headers)
    print(f"Fetched programs, status {response.status_code}")
    response.raise_for_status()
    data = response.json()
    if data.get("data") is None or "errors" in data:
        print("Invalid response:", data)
        raise RuntimeError("Failed to fetch programs")
    programs = data["data"]["viewer"]["projects"]["list"]
    if programs is None:
        raise RuntimeError("No programs returned")
    return programs


def _fetch_mock():
    """
    Получает список программ из локального json-server.
    Возвращает список словарей программ. Вызывает исключение при ошибке.
    """
    try:
        r = requests.get(f"{MOCK_URL}/db")          
        r.raise_for_status() 
        raw_data = r.json()                                
        
        programs = raw_data.get("data", {}).get("projects", {}).get("list")
        
            
        print(f"💡 Получено {len(programs)} моковых программ из {MOCK_URL}/db.")
        return programs
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сетевого запроса к моковому API ({MOCK_URL}/db): {e}")
        raise RuntimeError(f"Ошибка подключения к моковому API: {e}")
    except Exception as e:
        print(f"Непредвиденная ошибка при обработке ответа мокового API: {e}")
        raise RuntimeError(f"Непредвиденная ошибка в моковом API: {e}")
