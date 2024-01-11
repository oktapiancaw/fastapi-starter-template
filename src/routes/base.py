from fastapi import APIRouter

from src.routes.api import post


router = APIRouter()
router.include_router(post.app, prefix="/post", tags=["Post"])
