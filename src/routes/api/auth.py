from typing import cast, Annotated

from loguru import logger
from pydantic import TypeAdapter
from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from src.common import envs
from src.models.base import Token
from src.models.user import UserModel
from src.configs.auth import create_access_token, expired_time, timedelta, JWTBearer
from src.configs.db import MainMongo

app = APIRouter()
__main_collection = "user"


@app.post("/login")
async def login_for_access_token(
    req: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    try:
        mongo = cast(MainMongo, req.app.state.mongo)

        raw_user = mongo.db[__main_collection].find_one(
            {
                "status": {"$ne": "archive"},
                "$or": [
                    {"email": form_data.username},
                    {"username": form_data.username},
                ],
            }
        )
        if raw_user:
            user = TypeAdapter(UserModel).validate_python(raw_user)

            if user.verify_password(form_data.password):
                access_token_expires = timedelta(
                    minutes=envs.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
                )
                access_token = create_access_token(
                    data=user.safe, expires_delta=access_token_expires
                )
                return Token(
                    access_token=access_token,
                    token_type="bearer",
                    expiredOn=expired_time(access_token_expires).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception:
        logger.opt(exception=Exception).error("Failed login for access token")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed login for access token",
        )


@app.post("/data", dependencies=[Depends(JWTBearer())])
async def get_data(
    req: Request,
):
    try:
        credentials = req.state.credentials
        if credentials:
            return JSONResponse(status_code=status.HTTP_200_OK, content=credentials)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Session is invalid",
            },
        )
    except Exception:
        logger.opt(exception=Exception).error("Failed get session data")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed get session data",
        )


@app.post("/refresh", dependencies=[Depends(JWTBearer())])
async def refresh(
    req: Request,
) -> Token:
    try:
        credentials = req.state.credentials
        if credentials:
            access_token_expires = timedelta(
                minutes=envs.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = create_access_token(
                data=credentials, expires_delta=access_token_expires
            )
            return Token(
                access_token=access_token,
                token_type="bearer",
                expiredOn=expired_time(access_token_expires).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Session is invalid",
            },
        )
    except Exception:
        logger.opt(exception=Exception).error("Failed refresh access token")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed refresh access token",
        )
