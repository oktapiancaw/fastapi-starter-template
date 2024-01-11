from typing import Optional, Union

from pydantic import BaseModel, Field


class ConnectionMeta(BaseModel):
    host: Optional[str] = Field("localhost", description="Connection host")
    port: Optional[int] = Field(8000, description="Connection port")
    username: Optional[str] = Field(None)
    password: Optional[str] = Field(None)
    database: Optional[Union[str, int]] = Field(None, description="Database name")

    def url(self, base: str = "http", with_db: bool = True) -> str:
        if self.username:
            return f"{base}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database if with_db else ''}"
        return f"{base}://{self.host}:{self.port}/{self.database if with_db else ''}"


class SearchSchema(BaseModel):
    field: str = Field(..., description="Field name")
    value: str = Field(..., description="Value search")
