from rich.console import Console
from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.selectable import Select
from sqlalchemy import func
from datetime import datetime
from .logging import LogWriter


ModelT = TypeVar("ModelT")


class CRUDService(Generic[ModelT]):
    '''CRUD boilerplate with minimal abstraction'''

    def __init__(self, model: Type[ModelT]) -> None:
        self.model: Type[ModelT] = model
        self.logger = LogWriter(self.model.__tablename__)  # type: ignore

    async def delete_model(self, db: AsyncSession, db_model: ModelT) -> None:
        '''
            deletes a model from the database
        Arguments:
            db {AsyncSession} -- the database session
            db_model {ModelT} -- the model to be deleted
        '''
        await self.logger.info(f"DELETE: {db_model}", db)
        await db.delete(db_model)
        await db.commit()

    async def insert_model(
        self,
        model_obj: ModelT,
        db: AsyncSession,
        commit: bool = True,
        refresh: bool = False
    ) -> None:
        '''
        inserts a model into the database

        Arguments:
            model_obj {ModelT} -- the model to be inserted
            db {AsyncSession} -- the database session

        Keyword Arguments:
            commit {bool} -- whether to commit the transaction (default: {True})
            refresh {bool} -- whether to refresh the model after commit (default: {False})
        '''
        await self.logger.info(f"CREATE: {model_obj}", db)
        db.add(model_obj)
        if not commit:
            return
        await db.commit()
        if refresh:
            await db.refresh(model_obj)

    async def get_by(
        self,
        predicate: Any,
        session: AsyncSession,
        options: Optional[List] = None
    ) -> Optional[ModelT]:
        '''
        returns a model from the ModelT table in the database based on the predicate
        passed 

        Arguments:
            predicate {Any} -- the predicate to filter records by
            session {AsyncSession} -- the database session

        Keyword Arguments:
            options {Optional[List]} -- sqlalchemy options (default: {None})

        Returns:
            Optional[ModelT] -- the frist model that matches the predicate
        '''
        query = select(self.model).filter(predicate)
        if options:
            for option in options:
                query = query.options(option)

        result = await session.execute(query)
        output = result.scalars().first()
        await self.logger.info(f"READ: {output}", session)
        return output

    async def get_all(self, db: AsyncSession) -> List[ModelT]:
        '''
        returns all of the models from ModelT table in the database

        Arguments:
            db {AsyncSession} -- 

        Returns:
            List[ModelT] -- list of all the models
        '''
        await self.logger.info(f"READ_ALL", db)
        result = await db.execute(select(self.model))
        return list(result.scalars().all())

    async def get_limited(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        options: Optional[List] = None
    ) -> List[ModelT]:
        '''
        returns a limited number of models from the ModelT table in the database

        Arguments:
            db {AsyncSession} -- the database session
        Keyword Arguments:
            skip {int} -- the number of models to skip (default: {0})
            limit {int} -- the number of models to return (default: {100})
            options {Optional[List]} -- sqlalchemy options (default: {None})
        Returns:
            List[ModelT] 
        '''
        await self.logger.info(f"READ: (OFFSET={skip} LIMIT={limit}) models", db)
        query = select(self.model).offset(skip).limit(limit)
        if options:
            for option in options:
                query = query.options(option)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelT:
        '''creates a new model using the pydantic model schema

        Arguments:
            db {AsyncSession} -- the database session
            obj_in {dict} -- pydantic model schema (model_dump())

        Returns:
            ModelT -- the newly created model
        '''
        self.logger.debug(
            # type: ignore
            f"Object-Model: {obj_in} -> {self.model.__tablename__}" # type: ignore
        )
        db_model = self.model(**obj_in)
        await self.insert_model(db_model, db, commit=True, refresh=True)
        return db_model

    async def update(
        self,
        db: AsyncSession,
        db_model: ModelT,
        obj_in: dict
    ) -> ModelT:
        '''_summary_
        updates a model using the 'obj_in' in dictionary derived from the pydantic model schema
        Arguments:
            db: the database session
            db_model: the model updated
            obj_in: pydantic model schema (model_dump())
        Returns:
            the newly updated model
        '''
        await self.logger.info(f"UPDATE: {db_model} -> {obj_in}", db)
        for field, value in obj_in.items():
            if hasattr(db_model, field):
                setattr(db_model, field, value)

        await db.commit()
        await db.refresh(db_model)
        return db_model

    async def count_query_total(self, query: Select, db: AsyncSession) -> int:
        '''
        counts the total number of records in a query

        Arguments:
            query: the query to count
        Returns:
            the query with the count function applied
        '''
        count_query = query.with_only_columns(
            func.count(),
            maintain_column_froms=True
        ).order_by(None)
        result = await db.execute(count_query)
        total: int = result.scalar_one()  # retrieves the count directly
        return total

    async def run_query(self, statement: Select, db: AsyncSession) -> List[ModelT]:
        '''
        executes a query statement and returns the results

        Arguments:
            statement: the query statement
        Returns:
            the results of the query
        '''
        await self.logger.info(f"QUERY: {statement}", db)
        result = await db.execute(statement)
        return result.scalars().all()  # type: ignore
    