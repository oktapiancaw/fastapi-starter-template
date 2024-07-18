import uuid

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import RootModel, field_serializer


class PostMeta(SQLModel):
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    status: str = Field(nullable=False)
    published: Optional[bool] = Field(default=True, nullable=False)


class PostData(PostMeta, table=True):
    __tablename__ = "posts"

    id: uuid.UUID = Field(
        default_factory=lambda: uuid.uuid4(),
        primary_key=True,
        index=True,
        nullable=False,
    )
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(), nullable=True
    )
    updated_at: Optional[datetime] = Field(None, nullable=True)
    deleted_at: Optional[datetime] = Field(None, nullable=True)

    @field_serializer("id")
    def serialize_id(self, value):
        return str(value)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime):
        if value:
            return str(value.strftime("%Y-%m-%d %H:%M:%S"))

    @field_serializer("updated_at")
    def serialize_updated_at(self, value: datetime):
        if value:
            return str(value.strftime("%Y-%m-%d %H:%M:%S"))

    @field_serializer("deleted_at")
    def serialize_deleted_at(self, value: datetime):
        if value:
            return str(value.strftime("%Y-%m-%d %H:%M:%S"))


class PostList(RootModel):
    root: list[PostData]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __len__(self):
        return self.root.__len__()
