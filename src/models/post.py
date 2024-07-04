from uuid import uuid4
from typing import Optional
from datetime import datetime

from pydantic import (
    BaseModel,
    RootModel,
    ConfigDict,
    Field,
    model_validator,
    field_serializer,
    UUID4,
)
from sqlalchemy import (
    Column,
    Boolean,
    String,
    TIMESTAMP,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID


from src.models.base import Base


class PostOrm(Base):
    __tablename__ = "posts"

    # ? ID
    id = Column(
        UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True
    )

    # ? Base meta
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    published = Column(Boolean, default=True, nullable=False)

    # ? Time
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)


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
    id: UUID4 = Field(default_factory=lambda: uuid4())
    status: Optional[str] = "active"
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now())
    updated_at: Optional[datetime] = Field(None)
    deleted_at: Optional[datetime] = Field(None)

    @property
    def orm_structure(self) -> PostOrm:
        return PostOrm(**self.model_dump())

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


class PostView(PostData):

    model_config = ConfigDict(
        from_attributes=True,
    )


class PostViewList(RootModel):
    root: list[PostView]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __len__(self):
        return self.root.__len__()
