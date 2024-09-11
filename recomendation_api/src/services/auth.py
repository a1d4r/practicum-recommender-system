import http
import json
import time
from typing import Optional

from jose import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import get_settings

settings = get_settings()


def decode_token(token: str) -> Optional[dict]:
    try:
        decoded_token = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        decoded_token["sub"] = json.loads(decoded_token["sub"])
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except Exception:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, required_roles: list[str], auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.required_roles = required_roles

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN, detail="Invalid authorization code."
            )
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail="Only Bearer token might be accepted",
            )
        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN, detail="Invalid or expired token."
            )
        if self.required_roles and not any(
            role in self.required_roles for role in decoded_token["sub"]["roles"]
        ):
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail="Invalid role.")
        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> Optional[dict]:
        return decode_token(jwt_token)


def security_jwt(required_roles: list[str]):
    return JWTBearer(required_roles=required_roles)
