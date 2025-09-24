import logging
from typing import Any, Generic, NamedTuple, TypeVar

from sqlalchemy import Result, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

M = TypeVar('M', bound=DeclarativeBase | Any)




async def query_streamer(
    query: Select,
    db: AsyncSession,
    *,
    limit: int | None = None,
    offset: int | None = None,
):
    """
    Stream results of a query with optional limit, offset, and uniqueness.

    Parameters
    ----------
    query : Select
        _The SQLAlchemy select statement to execute_
    db : AsyncSession
        _The async database session_
    limit : int | None, optional
        _The maximum number of records to return_, by default None
    offset : int | None, optional
        _The number of records to skip_, by default None
    unique : bool, optional
        _Whether to ensure unique results_, by default True

    Yields
    ------
    _MappingResult | Any_
        _The result rows as mappings or models_
    """
    if limit is not None and limit > 0:
        query = query.limit(limit)

    if offset is not None and offset > 0:
        query = query.offset(offset)

    stream = await db.stream(query)

    async for row in stream.unique():
        yield row

def santize_str(val: str) -> str:
    return val.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')



class _SQLRepo(Generic[M]):
    model: type[M]

    def __init__(
        self,
        *,
        model: type[M] | None = None
    ) -> None:
        '''
        Accepts an AsyncSession and an optional model class, if not provided
        as a class variable.

        Parameters
        ----------
        db : AsyncSession
        model : type[M] | None, optional
            _The model to use if not defined in class_, by default None

        Raises
        ------
        ValueError
            _If no model is provided as a parameter or defined in class_
        '''
        if not model and not hasattr(self, 'model'):
            raise ValueError(
                'You must provide a model or set the model attribute.'
            )
        elif model:
            self.model = model

        self.logger = logging.getLogger(__name__)

    @property
    def table_name(self) -> str:
        return self.model.__tablename__

class SQLQuery(NamedTuple):
    statement: Select
    total: int


class ORMCommands(Generic[M]):
    '''
    A simple read-only repository for SQLAlchemy models.
    A session that can write is allowed, but no write methods
    are implemented.
    '''
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db


    async def first_dict(self, statement: Select) -> dict | None:
        result = await self.db.execute(statement)
        mapping = result.mappings().first()
        return dict(mapping) if mapping else None

    async def all_dicts(self, statement: Select) -> list[dict]:
        result = await self.db.execute(statement)
        return [dict(row) for row in result.mappings().all()] or []

    async def scalar(self, statement: Select) -> M | None:
        result = await self.db.execute(statement)
        return result.scalar()

    async def scalars_all(self, statement: Select) -> list[M]:
        result = await self.db.execute(statement)
        models = result.scalars().all()
        return list(models) if models else []

    async def scalars_one(self, statement: Select) -> M | None:
        result = await self.db.execute(statement)
        return result.scalars().one_or_none()

    async def stream_scalars(
        self,
        statement: Select,
        *,
        limit: int | None = None,
        offset: int | None = None
    ):
        async for row in query_streamer(
            statement,
            self.db,
            limit=limit,
            offset=offset
        ):
            yield row.scalar()

    async def stream_mappings(
        self,
        statement: Select,
        *,
        limit: int | None = None,
        offset: int | None = None
    ):
        async for row in query_streamer(
            statement,
            self.db,
            limit=limit,
            offset=offset
        ):
            yield dict(row.mappings())

    def safelike(self, unsafe_str: str, column) -> Any:
        safe_str = santize_str(unsafe_str)
        pattern = f'%{safe_str}%'
        return column.ilike(pattern, escape='\\')

    async def new_query(self, statement: Select, model) -> SQLQuery:
        total_stmnt = select(func.count()).select_from(model)
        if whereclause := statement._whereclause:  # type: ignore
            total_stmnt = total_stmnt.where(whereclause)

        total = await self.db.execute(total_stmnt)
        total = total.scalar_one_or_none() or 0
        return SQLQuery(
            statement=statement,
            total=total
        )

    async def save(
        self,
        *,
        commit: bool = False,
        flush: bool = True
    ) -> bool:
        try:
            if flush:
                await self.db.flush()

            if commit:
                await self.db.commit()

            return True
        except Exception as e:
            await self.db.rollback()
            return False

class SQLRepository(_SQLRepo[M]):

    def __init__(
        self,
        db: AsyncSession,
        *,
        model: type[M] | None = None
    ) -> None:
        super().__init__(model=model)
        self.db: AsyncSession = db
        self.cmds: ORMCommands[M] = ORMCommands(db)


    def insert(self, **kwargs) -> M:
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.logger.info(f'Created new {self.model.__tablename__} instance.')
        return instance

    def patch(self, model: M, **kwargs) -> None:
        try:
            for key, value in kwargs.items():
                setattr(model, key, value)
        except Exception as e:
            model_id = getattr(model, 'id', None) or 'unknown'
            self.logger.error(
                f'Error setting attributes on {self.model.__tablename__} '
                f'instance {model_id}',
                exc_info=e
            )
            raise

    async def create(self, **kwargs) -> M:
        instance = self.insert(**kwargs)
        await self.cmds.save(commit=True, flush=False)
        return instance

    async def update(self, model: M, **kwargs) -> M:
        self.patch(model, **kwargs)
        await self.cmds.save(commit=True, flush=False)
        await self.db.refresh(model)
        return model

    async def delete(self, model: M) -> bool:
        self.logger.info(
            f'Removing instance {model} from `{self.model.__tablename__}` ')
        try:
            await self.db.delete(model)
        except Exception as e:
            self.logger.error(f'Error removing {model}', exc_info=e)
            return False

        return True

    def was_successful(self, result: Result) -> bool:
        return result.rowcount is not None and result.rowcount > 0 # type: ignore


    



