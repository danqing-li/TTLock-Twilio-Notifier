import os
import hashlib
import requests
from dataclasses import dataclass
from typing import Optional

TTLOCK_BASE_URL = os.getenv("TTLOCK_BASE_URL", "https://api.sciener.com")
TTLOCK_TOKEN_URL = f"{TTLOCK_BASE_URL}/oauth2/token"
TTLOCK_EKEY_ADD_PATH = "/v3/key/add"

@dataclass
class TTLockConfig:
    client_id: str
    client_secret: str
    username: Optional[str] = None
    password_md5: Optional[str] = None

class TTLockClient:
    def __init__(self, config: TTLockConfig, access_token=None, refresh_token=None):
        self.config = config
        self.access_token = access_token
        self.refresh_token = refresh_token

    @staticmethod
    def md5_lower(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    @classmethod
    def from_env(cls):
        client_id = os.environ.get("TTLOCK_CLIENT_ID")
        client_secret = os.environ.get("TTLOCK_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise ValueError(
                "TTLOCK_CLIENT_ID and TTLOCK_CLIENT_SECRET must be set in the environment."
            )

        access_token = os.environ.get("TTLOCK_ACCESS_TOKEN")
        refresh_token = os.environ.get("TTLOCK_REFRESH_TOKEN")

        username = os.environ.get("TTLOCK_USERNAME")
        password = os.environ.get("TTLOCK_PASSWORD")
        password_md5 = cls.md5_lower(password) if password else None

        config = TTLockConfig(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password_md5=password_md5,
        )

        if access_token:
            return cls(config, access_token=access_token, refresh_token=refresh_token)

        if not username or not password_md5:
            raise ValueError(
                "TTLOCK_ACCESS_TOKEN is not set. Provide TTLOCK_USERNAME and TTLOCK_PASSWORD to obtain a token, or set TTLOCK_ACCESS_TOKEN manually."
            )

        return cls(config)

    def token_payload(self, grant_type="password"):
        if grant_type == "password":
            if not self.config.username or not self.config.password_md5:
                raise ValueError(
                    "Username/password are required for password grant."
                )

        return {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": grant_type,
            "username": self.config.username,
            "password": self.config.password_md5,
        }

    def get_access_token(self):
        resp = requests.post(TTLOCK_TOKEN_URL, data=self.token_payload(), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token")
        return data

    def refresh_access_token(self):
        if not self.refresh_token:
            raise ValueError("refresh_token is missing")
        resp = requests.post(TTLOCK_TOKEN_URL, data={
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token", self.refresh_token)
        return data

    def _request(self, method, path, params=None, data=None):
        if not self.access_token:
            self.get_access_token()
        params = params or {}
        params.update({
            "clientId": self.config.client_id,
            "accessToken": self.access_token,
        })
        url = f"{TTLOCK_BASE_URL}{path}"
        resp = requests.request(method, url, params=params, data=data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_ekey(self, key_id: int):
        return self._request("GET", "/v3/key/get", params={"keyId": key_id})

    def list_ekeys(self, lock_id: int, page_no=1, page_size=20):
        return self._request(
            "GET",
            "/v3/lock/listKey",
            params={"lockId": lock_id, "pageNo": page_no, "pageSize": page_size},
        )

    def get_passcode(self, keyboard_pwd_id: int):
        return self._request("GET", "/v3/keyboardPwd/get", params={"keyboardPwdId": keyboard_pwd_id})

    def list_passcodes(self, lock_id: int, page_no=1, page_size=20):
        return self._request(
            "GET",
            "/v3/lock/listKeyboardPwd",
            params={"lockId": lock_id, "pageNo": page_no, "pageSize": page_size},
        )

    def create_passcode(self, lock_id: int, keyboard_pwd_name: str, keyboard_pwd: str, start_date: int, end_date: int):
        data = {
            "lockId": lock_id,
            "keyboardPwdName": keyboard_pwd_name,
            "keyboardPwd": keyboard_pwd,
            "startDate": start_date,
            "endDate": end_date,
            "keyboardPwdVersion": 4,
            "keyboardPwdType": 3,
            "shareKeyStatus": 1,
        }
        return self._request("POST", "/v3/keyboardPwd/add", data=data)

    def create_ekey(
        self,
        lock_id: int,
        start_date: int,
        end_date: int,
        ekey: str,
        key_right: int = 1,
        keyboard_pwd_version: int = 4,
        remote_enable: int = 1,
        remarks: str = "",
    ):
        data = {
            "lockId": lock_id,
            "startDate": start_date,
            "endDate": end_date,
            "ekey": ekey,
            "keyRight": key_right,
            "keyboardPwdVersion": keyboard_pwd_version,
            "remoteEnable": remote_enable,
            "remarks": remarks,
        }
        return self._request("POST", TTLOCK_EKEY_ADD_PATH, data=data)