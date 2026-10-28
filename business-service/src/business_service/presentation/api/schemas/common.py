from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class StrictModel(BaseModel):
    """Request bodies reject unknown fields such as id or status."""

    model_config = ConfigDict(extra="forbid")


class PageResponse[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int


class Problem(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str
    errors: list[dict] | None = Field(default=None)
