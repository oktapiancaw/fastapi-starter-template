import traceback

from datetime import timedelta, datetime, timezone

import jwt

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.common import envs


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme.",
                )

            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token.",
                )
            request.state.credentials = self.decodeJWT(credentials.credentials)
            return credentials.credentials
        else:
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code.",
            )

    def decodeJWT(self, token: str) -> dict:
        try:
            decoded_token = jwt.decode(
                token, envs.AUTH_SECRET_KEY, algorithms=envs.AUTH_ALGORITHM
            )
            return decoded_token
        except:
            traceback.print_exc()
            return {}

    def verify_jwt(self, jwtoken: str) -> bool:

        try:
            jwtoken = jwtoken.replace("Bearer ", "")
            payload = self.decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            if payload["exp"] >= datetime.now().timestamp():
                return True
            return False
        return False


def expired_time(expires_delta: timedelta):
    expire = datetime.now(timezone.utc) + expires_delta
    return expire


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = expired_time(expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, envs.AUTH_SECRET_KEY, algorithm=envs.AUTH_ALGORITHM
    )
    return encoded_jwt
