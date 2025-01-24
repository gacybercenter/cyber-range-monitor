from enum import StrEnum
from pydantic import BaseModel
from typing import Optional, Any


class BaseQueryResults:
    total_rows: int
    statement_str: str
    result: list[dict]
    page_size: int
    columns: list[str]


class QueryResults(BaseQueryResults):
    '''
    Assists with the display of query results in a paginated format 

    Arguments:
        BaseQueryResults {_type_} -- _description_
    '''

    def __init__(
        self,
        row_count: int,
        statement_str: str,
        page: list[dict],
        col_names: list[str],
        page_size: int
    ) -> None:
        self.total_rows = row_count
        self.statement_str = statement_str
        self.page_size = page_size
        self.columns = col_names
        self.result = page


class TableInfo(BaseModel):
    model_prefix: str
    table_name: str
    columns: list[str]
    size: int
    schema: Optional[str] = None
