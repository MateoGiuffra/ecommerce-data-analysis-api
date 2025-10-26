from pydantic import BaseModel, Field
from fastapi import Query
from typing import List, Generic, TypeVar


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)  
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

def get_page_params(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Elements per page"), 
) -> PageParams:
    return PageParams(page=page, limit=limit)

ResultType = TypeVar("ResultType")

class PageResponse(BaseModel, Generic[ResultType]):
    model_config = {"from_attributes": True}
    results: List[ResultType]
    page: int
    limit: int
    total_pages: int
    total_results: int