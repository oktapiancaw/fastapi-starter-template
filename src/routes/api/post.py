from typing import cast

from loguru import logger
from pydantic import TypeAdapter
from fastapi import APIRouter, Request, HTTPException, Path, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from src.configs.db import MainPostgre
from src.models.base import SearchSchema
from src.models.post import PostMeta, PostData, PostView, PostViewList, PostOrm

app = APIRouter()
__main_collection = PostOrm.__tablename__


@app.get("/{id}")
def get_post(req: Request, id: str = Path(...)):
    try:
        postgre = cast(MainPostgre, req.app.state.postgre)

        raw = postgre.client.query(PostOrm).where(PostOrm.id == id).first()
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
        postgre = cast(MainPostgre, req.app.state.postgre)

        raw = postgre.client.query(PostOrm).where(PostOrm.status != "archive").all()
        # * Validation if post is exists
        if raw:
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
        postgre = cast(MainPostgre, req.app.state.postgre)

        count = postgre.client.execute(
            text(
                f"""SELECT COUNT(id) FROM public."{__main_collection}" WHERE status<>\'archive\'"""
            )
        ).scalar()
        raw = (
            postgre.client.query(PostOrm)
            .where(PostOrm.status != "archive")
            .where(text(f"{search.field} ILIKE '%{search.value}%'"))
            .all()
        )
        # * Validation if post is exists
        if raw:
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
        postgre = cast(MainPostgre, req.app.state.postgre)

        payload = TypeAdapter(PostData).validate_python(data.model_dump())

        postgre.client.add(payload.orm_structure)
        postgre.client.commit()

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": status.HTTP_201_CREATED,
                "message": "Success add post",
                "data": {"id": str(payload.id)},
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
        postgre = cast(MainPostgre, req.app.state.postgre)

        raw = postgre.client.query(PostOrm).where(PostOrm.id == id).first()
        if raw:
            postgre.client.query(PostOrm).where(PostOrm.id == id).update(
                data.model_dump(exclude_none=True)
            )
            postgre.client.commit()

            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content={
                    "status": status.HTTP_202_ACCEPTED,
                    "message": "Success edit post",
                    "data": {"id": id},
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
        postgre = cast(MainPostgre, req.app.state.postgre)

        raw = postgre.client.query(PostOrm).where(PostOrm.id == id).first()
        if raw:
            postgre.client.query(PostOrm).where(PostOrm.id == id).update(
                {"status": "archive"}
            )
            postgre.client.commit()

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": status.HTTP_200_OK,
                    "message": "Success delete post",
                    "data": {"id": id},
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
