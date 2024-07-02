from uuid import uuid4
from typing import Optional
from datetime import datetime

from fastapi import Response
from pydantic import BaseModel, RootModel, Field, ConfigDict


class PostMeta(BaseModel):
    title: str = Field(..., description="Title post")
    content: str = Field(..., description="Content post")
    published: Optional[bool] = Field(default=True, description="Published post")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "title": "Title post",
                "content": "Content post",
                "published": True,
            }
        },
    )


class PostData(PostMeta):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    status: Optional[str] = "active"
    createdAt: Optional[int] = Field(
        default_factory=lambda: int(datetime.now().timestamp() * 1000), ge=0
    )
    updatedAt: Optional[int] = Field(None)
    deletedAt: Optional[int] = Field(None)

    @property
    def save_mongo(self):
        return self.model_dump(by_alias=True, exclude_none=True)

    @property
    def update_mongo(self):
        self.createdAt = int(datetime.now().timestamp() * 1000)
        return self.model_dump(
            by_alias=True, exclude_none=True, exclude={"id", "createdAt"}
        )

    @property
    def delete_mongo(self):
        self.deletedAt = int(datetime.now().timestamp() * 1000)
        self.status = "archive"
        return self.model_dump(
            by_alias=True, exclude_none=True, exclude={"id", "createdAt"}
        )


class PostView(PostData): ...


class PostViewList(RootModel):
    root: list[PostView]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __len__(self):
        return self.root.__len__()


# PostViewList = RootModel[list[PostView]]
