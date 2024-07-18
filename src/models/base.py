import re

from typing import Optional, Union

from pydantic import BaseModel, Field, model_validator


class DatabaseConnectionMeta(BaseModel):

    host: Optional[str] = Field("localhost", description="Connection host")
    port: Optional[Union[str, int]] = Field(8000, description="Connection port")
    username: Optional[str] = Field(None)
    password: Optional[str] = Field(None)
    database: Optional[Union[str, int]] = Field(None, description="Database name")

    uri: Optional[str] = Field("", description="")

    def uri_string(self, base: str = "http", with_db: bool = True) -> str:
        meta = f"{self.host}:{self.port}"
        if self.username:
            return f"{base}://{self.username}:{self.password}@{meta}/{self.database if with_db else ''}"
        return f"{base}://{meta}/{self.database if with_db else ''}"

    @model_validator(mode="after")
    def extract_uri(self):
        if self.uri:
            uri = re.sub(r"\w+:(//|/)", "", self.uri)
            metadata, others = (
                re.split(r"\/\?|\/", uri) if re.search(r"\/\?|\/", uri) else [uri, None]
            )
            if others and "&" in others:
                for other in others.split("&"):
                    if "=" in other and re.search(r"authSource", other):
                        self.database = other.split("=")[-1]
                    elif "=" not in other:
                        self.database = other
            if "@" in metadata:
                self.username, self.password, self.host, self.port = re.split(
                    r"\@|\:", metadata
                )
            else:
                self.host, self.port = re.split(r"\:", metadata)
            self.port = int(self.port)
        return self


class SearchSchema(BaseModel):
    field: str = Field(..., description="Field name")
    value: str = Field(..., description="Value search")
