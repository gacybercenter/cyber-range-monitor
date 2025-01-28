from typing import TypeVar, Generic, Any, Type, Optional
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from pathlib import Path

from app.core.db import init_db
from app.services.mixins import CRUDService
from app.models import model_map
from cli.context.defaults import insert_table_defaults

from cli.misc.cli_types import TableInfo, QueryResults


def unknown_model(cmd_input: str) -> Exception:
    msg = f"Invalid model prefix '{
        cmd_input}', please choose from {model_map.keys()}"
    return ValueError(msg)


ModelT = TypeVar('ModelT', bound=DeclarativeBase)


class CLIModelController(Generic[ModelT]):
    '''
    The readonly controller for the database in the CLI 
    and contains all of the utility methods for manipulating
    the SQLAlchemy ORM objects. A single instance represents 
    a single controller for an ORM.
    '''

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model_type: Type[ModelT] = self._get_orm()
        self.controller = self._get_controller()

    @staticmethod
    def list_model_names() -> list[str]:
        return [model for model in model_map.keys()]

    def _get_orm(self) -> Type[ModelT]:
        model_type = model_map.get(self.model_name)
        if not model_type:
            raise unknown_model(self.model_name)
        return model_type

    def _get_controller(self) -> CRUDService:
        return CRUDService(self.model_type)  # type: ignore

    def inspect_schema(self) -> Optional[str]:
        return self.model_type.__table__.schema

    async def get_id(self, id: int, session: AsyncSession) -> str:
        if not hasattr(self.model_type, 'id'):
            raise ValueError(
                f"Model '{self.model_name}' does not have an 'id' field"
            )

        result = await self.controller.get_by(
            session,
            self.model_type.id == id  # type: ignore
        )
        if not result:
            return f"No record found with id '{id}'"
        return str(result)

    async def get_result(self, limit: int, stmnt: Select, db: AsyncSession) -> QueryResults:
        query_total = await self.controller.count_query_total(stmnt, db)
        if query_total == 0:
            return QueryResults(
                row_count=0,
                statement_str=str(stmnt),
                page=[],
                page_size=limit,
                col_names=[c.name for c in self.model_type.__table__.columns]
            )
        query = stmnt.limit(limit)
        results = await self.controller.execute_statement(query, db)
        result = [self.serialize(row) for row in results]
        return QueryResults(
            row_count=query_total,
            statement_str=str(stmnt),
            page=result,
            page_size=limit,
            col_names=[c.name for c in self.model_type.__table__.columns]
        )

    async def read_all(self, limit: int, db: AsyncSession) -> QueryResults:
        stmnt = select(self.model_type).limit(limit)
        results = await self.get_result(limit, stmnt, db)
        return results

    async def total_records(self, db: AsyncSession) -> int:
        return await self.controller.count_query_total(select(self.model_type), db)

    @staticmethod
    def create_controller(model_name: str) -> 'CLIModelController':
        return CLIModelController(model_name)

    def serialize(self, model_instance: ModelT) -> dict[str, Any]:
        return {c.name: getattr(model_instance, c.name) for c in model_instance.__table__.columns}

    async def table_info_meta(self, include_schema: bool, db: AsyncSession) -> TableInfo:
        size = await self.total_records(db)
        columns = [c.name for c in self.model_type.__table__.columns]
        table_name = self.model_type.__tablename__
        schema = None
        if include_schema:
            schema = self.inspect_schema()
        return TableInfo(
            model_prefix=self.model_name,
            table_name=table_name,
            columns=columns,
            size=size,
            schema=schema
        )

    @staticmethod
    async def get_table_metas(include_schemas: bool, db: AsyncSession) -> list[TableInfo]:
        table_metas = []
        for orm in model_map.keys():
            model_controller = CLIModelController.create_controller(orm)
            meta = await model_controller.table_info_meta(include_schemas, db)
            table_metas.append(meta)
        return table_metas


def db_exists() -> bool:
    db_dir = Path('instance')
    return db_dir.exists()


async def initialize_database(insert_defaults: bool = True) -> None:
    if not db_exists():
        Path('instance').mkdir()
    await init_db()
    if insert_defaults:
        async with AsyncSession() as session:
            await insert_table_defaults(session)

async def reinit_database(insert_defaults: bool = True) -> None:
    db_file = Path('instance', 'app.db')
    if not db_file.exists():
        raise FileNotFoundError(
            "Database has not been initialized and cannot be re-initialized"
        )

    db_file.unlink()
    await initialize_database(insert_defaults=insert_defaults)
