import json
import base64
from datetime import datetime, timedelta
import requests
from config import TUMAR_API_URL, TOKENS_FILE

class AuthService:
    """
    Отвечает за получение, хранение и обновление JWT-токенов.
    """

    def __init__(self, code: str):
        self.code = code
        self.access_token = None
        self.refresh_token = None
        self.expiry: datetime = datetime.utcnow()
        print("[INIT] Starting AuthService with code")
        self._load_or_login()

    def _load_or_login(self):
        """Пытается загрузить токены из файла, иначе делает первичный ConfirmLogin."""
        try:
            with open(TOKENS_FILE, "r") as f:
                data = json.load(f)
            self.access_token = data["accessToken"]
            self.refresh_token = data["refreshToken"]
            self.expiry = self._decode_exp(self.access_token)
            print("[AUTH] Tokens loaded from file.")
        except (FileNotFoundError, KeyError, ValueError) as e:
            print(f"[AUTH] Failed to load tokens from file: {e}. Trying ConfirmLogin...")
            self._confirm_login()

    def _confirm_login(self):
        """Первичный запрос ConfirmLogin(code) → access + refresh."""
        print("[AUTH] Sending ConfirmLogin mutation...")
        payload = {
            "operationName": "ConfirmLogin",
            "query": (
                "mutation ConfirmLogin($code: String!) {"
                "  users {"
                "    confirmLogin(code: $code) {"
                "      token { accessToken refreshToken }"
                "    }"
                "  }"
                "}"
            ),
            "variables": {"code": self.code},
        }
        resp = requests.post(TUMAR_API_URL, json=payload)
        resp.raise_for_status()
        tok = resp.json()["data"]["users"]["confirmLogin"]["token"]
        print("[AUTH] Received tokens from ConfirmLogin.")
        self._save_tokens(tok["accessToken"], tok["refreshToken"])

    def _decode_exp(self, token: str) -> datetime:
        """Декодирует payload JWT и возвращает datetime expiration."""
        print("[TOKEN] Decoding token expiration...")
        _, payload_b64, _ = token.split(".")
        payload_b64 += "=" * (-len(payload_b64) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload_b64))
        exp = datetime.utcfromtimestamp(data["exp"])
        print(f"[TOKEN] Token expires at {exp} UTC")
        return exp

    def _save_tokens(self, access: str, refresh: str):
        """Сохраняет токены в экземпляр и на диск."""
        self.access_token = access
        self.refresh_token = refresh
        self.expiry = self._decode_exp(access)
        with open(TOKENS_FILE, "w") as f:
            json.dump({
                "accessToken": self.access_token,
                "refreshToken": self.refresh_token
            }, f)
        print("[AUTH] Tokens saved to disk.")

    def _needs_refresh(self, buffer_seconds: int = 60) -> bool:
        """Проверяет, не истечёт ли access_token в ближайшие buffer_seconds."""
        need = datetime.utcnow() + timedelta(seconds=buffer_seconds) >= self.expiry
        print(f"[CHECK] Token needs refresh: {need}")
        return need

    def refresh(self):
        """Делает GraphQL‑мутацию refresh(refreshToken) → новую пару токенов."""
        print("[AUTH] Sending refresh mutation...")
        payload = {
            "operationName": None,
            "query": (
                "mutation ($refreshToken: String!) {"
                "  users {"
                "    refresh(refreshToken: $refreshToken) { accessToken refreshToken }"
                "  }"
                "}"
            ),
            "variables": {"refreshToken": self.refresh_token},
        }
        headers = {"Authorization": f"Bearer {self.access_token}"}
        resp = requests.post(TUMAR_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        tok = resp.json()["data"]["users"]["refresh"]
        print("[AUTH] Refresh successful, tokens updated.")
        self._save_tokens(tok["accessToken"], tok["refreshToken"])

    def get_access_token(self) -> str:
        """
        Возвращает валидный access_token, обновляя его, если срок почти истёк.
        """
        print("[TOKEN] get_access_token called")
        if self._needs_refresh():
            print("[TOKEN] Token expired or near expiry, refreshing...")
            self.refresh()
        else:
            print("[TOKEN] Token still valid.")
        return self.access_token
