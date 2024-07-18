from typing import cast

from loguru import logger
from fastapi import APIRouter, Request, HTTPException, Path, status
from fastapi.responses import JSONResponse
from sqlmodel import select, text

from src.configs.db import MainPostgre
from src.models.base import SearchSchema
from src.models.post import PostMeta, PostData

app = APIRouter()


@app.get("/{id}", response_model=PostData)
def get_post(req: Request, id: str = Path(...)):
    try:
        postgre = cast(MainPostgre, req.app.state.postgre)

        statement = (
            select(PostData)
            .where(PostData.status != "archive")
            .where(PostData.id == id)
        )
        result = postgre.client.exec(statement).first()
        if result:
            return result
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


@app.get("", response_model=list[PostData])
def get_all_posts(req: Request):
    try:
        postgre = cast(MainPostgre, req.app.state.postgre)

        statement = select(PostData).where(PostData.status != "archive")
        result = postgre.client.exec(statement).all()
        if result:
            return result
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


@app.post("/search", response_model=list[PostData])
def search_posts(req: Request, search: SearchSchema):
    try:
        postgre = cast(MainPostgre, req.app.state.postgre)

        statement = (
            select(PostData)
            .where(PostData.status != "archive")
            .where(text(f"{search.field} ILIKE '%{search.value}%'"))
        )
        result = postgre.client.exec(statement).all()
        if result:
            return result
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


@app.post("", response_model=PostData, status_code=status.HTTP_201_CREATED)
def add_post(req: Request, data: PostMeta):
    try:
        postgre = cast(MainPostgre, req.app.state.postgre)

        payload = PostData.model_validate(data)
        postgre.client.add(payload)
        postgre.client.commit()
        postgre.client.refresh(payload)

        return payload
    except Exception:
        logger.opt(exception=Exception).error("Failed add post")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed add post"
        )


@app.put("/{id}", response_model=PostMeta)
def edit_post(req: Request, data: PostMeta, id: str = Path(...)):
    try:
        postgre = cast(MainPostgre, req.app.state.postgre)

        post_data = postgre.client.get(PostData, id)
        if post_data:
            post_data.sqlmodel_update(data)
            postgre.client.add(post_data)
            postgre.client.commit()
            postgre.client.refresh(post_data)

            return post_data

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


@app.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(req: Request, id: str = Path(...)):
    try:
        postgre = cast(MainPostgre, req.app.state.postgre)

        post_data = postgre.client.get(PostData, id)
        if post_data:
            postgre.client.delete(post_data)
            postgre.client.commit()
            return

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
