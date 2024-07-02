from typing import cast

from loguru import logger
from pydantic import TypeAdapter
from fastapi import APIRouter, Request, HTTPException, Path, status
from fastapi.responses import JSONResponse

from src.configs.db import MainMongo
from src.models.base import SearchSchema
from src.models.post import PostMeta, PostData, PostView, PostViewList

app = APIRouter()
__main_collection = "post"


@app.get("/{id}")
def get_post(req: Request, id: str = Path(...)):
    try:
        mongo = cast(MainMongo, req.app.state.mongo)

        raw = mongo.db[__main_collection].find_one(
            {"_id": id, "status": {"$ne": "archive"}}
        )
        if raw:
            payload = TypeAdapter(PostView).validate_python(raw)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": status.HTTP_200_OK,
                    "message": "Success get all post",
                    "data": payload.model_dump(),
                },
            )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Post is not found",
            },
        )

    except Exception:
        logger.opt(exception=Exception).error("Failed get post")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed get post"
        )


@app.get("s")
def get_all_posts(req: Request):
    try:

        # ? Get mongo from lifespan
        mongo = cast(MainMongo, req.app.state.mongo)

        raw = mongo.db[__main_collection].find({"status": {"$ne": "archive"}})
        # * Validation if post is exists
        if list(raw):
            # * Transform post model
            payloads = TypeAdapter(PostViewList).validate_python(raw)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": status.HTTP_200_OK,
                    "message": "Success get all post",
                    "data": payloads.model_dump(),
                    "metadata": {"size": payloads.__len__()},
                },
            )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Post is not found",
            },
        )

    except Exception:
        logger.opt(exception=Exception).error("Failed get all post")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed get all post",
        )


@app.post("s/search")
def search_posts(req: Request, search: SearchSchema):
    try:
        mongo = cast(MainMongo, req.app.state.mongo)
        query = {"status": {"$ne": "archive"}}
        count = mongo.db[__main_collection].count_documents(query)
        raw = mongo.db[__main_collection].find(
            query.update({search.field: {"$regex": search.value}})
        )

        # * Validation if post is exists
        if list(raw):
            # * Transform post model
            payloads = TypeAdapter(PostViewList).validate_python(raw)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": status.HTTP_200_OK,
                    "message": "Success get all post",
                    "data": payloads.model_dump(),
                    "metadata": {"size": count, "totalItems": payloads.__len__()},
                },
            )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Post is not found",
            },
        )

    except Exception:
        logger.opt(exception=Exception).error("Failed get all post")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed get all post",
        )


@app.post("")
def add_post(req: Request, data: PostMeta):
    try:
        mongo = cast(MainMongo, req.app.state.mongo)

        payload = TypeAdapter(PostData).validate_python(data.model_dump())

        mongo.db[__main_collection].insert_one(payload.save_mongo)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": status.HTTP_201_CREATED,
                "message": "Success add post",
                "data": {"id": payload.id},
            },
        )
    except Exception:
        logger.opt(exception=Exception).error("Failed add post")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed add post"
        )


@app.put("/{id}")
def edit_post(req: Request, data: PostMeta, id: str = Path(...)):
    try:
        mongo = cast(MainMongo, req.app.state.mongo)

        raw = mongo.db[__main_collection].find_one({"_id": id})
        if raw:
            payload = TypeAdapter(PostData).validate_python(data.model_dump())

            mongo.db[__main_collection].update_one(
                {"_id": id}, {"$set": payload.update_mongo}
            )

            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content={
                    "status": status.HTTP_202_ACCEPTED,
                    "message": "Success edit post",
                    "data": {"id": payload.id},
                },
            )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Post is not found",
            },
        )
    except Exception:
        logger.opt(exception=Exception).error("Failed edit post")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed edit post"
        )


@app.delete("/{id}")
def delete_post(req: Request, id: str = Path(...)):
    try:
        mongo = cast(MainMongo, req.app.state.mongo)

        raw = mongo.db[__main_collection].find_one({"_id": id})
        if raw:
            payload = TypeAdapter(PostData).validate_python(raw)

            mongo.db[__main_collection].update_one(
                {"_id": id}, {"$set": payload.delete_mongo}
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": status.HTTP_200_OK,
                    "message": "Success delete post",
                    "data": {"id": payload.id},
                },
            )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": status.HTTP_404_NOT_FOUND,
                "message": "Post is not found",
            },
        )
    except Exception:
        logger.opt(exception=Exception).error("Failed delete post")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed delete post",
        )
