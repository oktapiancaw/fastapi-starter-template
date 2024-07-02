from fastapi import APIRouter, Request, Depends

from src.configs.auth import JWTBearer
from src.routes.api import post, auth


router = APIRouter()


# ! Delete or comment this after use
@router.post("/admin/seed", tags=["Seed"])
def amdin_seed(req: Request):
    """
    Delete or comment this after use
    """
    from typing import cast

    from faker import Faker
    from fastapi import status
    from fastapi.responses import JSONResponse

    from src.models.user import UserModel
    from src.configs.db import MainMongo

    mongo = cast(MainMongo, req.app.state.mongo)

    fake = Faker()
    password = fake.password()
    payload = UserModel(
        name=fake.name(),
        username=fake.user_name(),
        email=fake.email(),
        password=password,
    ).hash_password()
    mongo.db["user"].insert_one(payload.model_dump(by_alias=True))

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "status": status.HTTP_201_CREATED,
            "message": "Success add post",
            "data": {**payload.model_dump(by_alias=True), "reveal_password": password},
        },
    )


router.include_router(auth.app, prefix="/auth", tags=["Auth"])
router.include_router(
    post.app, prefix="/post", tags=["Post"], dependencies=[Depends(JWTBearer())]
)
