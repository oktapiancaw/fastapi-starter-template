from uuid import uuid4
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class PostMeta(BaseModel):
    title: str = Field(..., description="Title post")
    content: str = Field(..., description="Content post")
    published: Optional[bool] = Field(default=True, description="Published post")


class PostData(PostMeta):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    status: Optional[str] = "active"
    createdAt: Optional[int] = Field(
        default_factory=lambda: int(datetime.now().timestamp() * 1000), ge=0
    )
    updatedAt: Optional[int] = Field(None)
    deletedAt: Optional[int] = Field(None)

    @property
    def save_mongo(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)

    @property
    def update_mongo(self) -> dict:
        self.createdAt = int(datetime.now().timestamp() * 1000)
        return self.model_dump(
            by_alias=True, exclude_none=True, exclude={"id", "createdAt"}
        )

    @property
    def update_mongo(self) -> dict:
        self.deletedAt = int(datetime.now().timestamp() * 1000)
        self.status = "archive"
        return self.model_dump(
            by_alias=True, exclude_none=True, exclude={"id", "createdAt"}
        )


class PostView(PostData):
    ...
