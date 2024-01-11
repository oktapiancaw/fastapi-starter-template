from typing import cast

from loguru import logger
from pydantic import TypeAdapter
from fastapi import APIRouter, Request, Path, HTTPException
from fastapi.responses import JSONResponse

from src.configs.db import MainMongo
from src.models.base import SearchSchema
from src.models.post import PostMeta, PostData, PostView

app = APIRouter()


@app.get("/get-one/{id}")
def get_post(req: Request, id: str = Path(...)):
    try:
        mongo = cast(MainMongo, req.app.state.mongo)

        raw = mongo.conn["template"].find_one({"_id": id, "status": {"$ne": "archive"}})
        if raw:
            payload = TypeAdapter(PostView).validate_python(raw)
            return payload

        return JSONResponse(status_code=404, content="Data is not found")
    except Exception:
        logger.opt(exception=Exception).error("Failed get post")
        return HTTPException(status_code=500, detail="Failed get post")


@app.get("/get-all")
def get_all_posts(req: Request):
    try:
        # ? Get mongo from lifespan
        mongo = cast(MainMongo, req.app.state.mongo)

        # * Validation if post is exists
        raw = mongo.conn["template"].find({"status": {"$ne": "archive"}})
        posts = list(raw)
        if posts:
            # * Transform post model
            payloads = TypeAdapter(list[PostView]).validate_python(posts)
            return payloads

        return JSONResponse(status_code=404, content="Data is not found")
    except Exception:
        logger.opt(exception=Exception).error("Failed get all post")
        return HTTPException(status_code=500, detail="Failed get all post")


@app.post("/search")
def search_posts(req: Request, search: SearchSchema):
    try:
        mongo = cast(MainMongo, req.app.state.mongo)

        raw = mongo.conn["template"].find(
            {
                "status": {
                    "$ne": "archive",
                },
                search.field: {"$regex": search.value},
            }
        )
        posts = list(raw)
        if posts:
            payloads = TypeAdapter(list[PostView]).validate_python(posts)
            return payloads

        return JSONResponse(status_code=404, content="Data is not found")
    except Exception:
        logger.opt(exception=Exception).error("Failed get all post")
        return HTTPException(status_code=500, detail="Failed get all post")


@app.post("/add")
def add_post(req: Request, data: PostMeta):
    try:
        mongo = cast(MainMongo, req.app.state.mongo)

        payload = TypeAdapter(PostData).validate_python(data.model_dump())

        mongo.conn["template"].insert_one(payload.save_mongo)

        return payload.id
    except Exception:
        logger.opt(exception=Exception).error("Failed add post")
        return HTTPException(status_code=500, detail="Failed add post")


@app.put("/edit/{id}")
def edit_post(req: Request, data: PostMeta, id: str = Path(...)):
    try:
        mongo = cast(MainMongo, req.app.state.mongo)

        raw = mongo.conn["template"].find_one({"_id": id})
        if raw:
            payload = TypeAdapter(PostData).validate_python(data.model_dump())

            mongo.conn["template"].update_one(
                {"_id": id}, {"$set": payload.update_mongo}
            )

            return payload.id

        return JSONResponse(status_code=404, content="Data is not found")
    except Exception:
        logger.opt(exception=Exception).error("Failed edit post")
        return HTTPException(status_code=500, detail="Failed edit post")


@app.delete("/delete/{id}")
def delete_post(req: Request, id: str = Path(...)):
    try:
        mongo = cast(MainMongo, req.app.state.mongo)

        raw = mongo.conn["template"].find_one({"_id": id})
        if raw:
            payload = TypeAdapter(PostData).validate_python(raw)

            mongo.conn["template"].update_one(
                {"_id": id}, {"$set": payload.delete_mongo}
            )

            return payload.id

        return JSONResponse(status_code=404, content="Data is not found")
    except Exception:
        logger.opt(exception=Exception).error("Failed delete post")
        return HTTPException(status_code=500, detail="Failed delete post")
