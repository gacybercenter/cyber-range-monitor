from typing import Annotated, Any, Generic, TypeVar

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.selectable import Select
from sqlalchemy.ext.asyncio import AsyncSession



ModelT = TypeVar("ModelT")  # TODO add base as bound to model T


class ModelRepository(Generic[ModelT]):
    """Provides methods for common CRUD operations on database models
    and is the foundation for all services that interact with the database.
    Properties:
        model {ModelT} -- the SQLAlchemy model class for the repository
        db {AsyncSession} -- the database session to use for queries
    """

    def __init__(self, model: type[ModelT], db: AsyncSession) -> None:
        self.model: type[ModelT] = model
        self.db: AsyncSession = db

    async def delete(self, db_model: ModelT) -> None:
        """ deletes a model from the database
        Arguments:
            db_model {ModelT} -- the model to be deleted
        """
        await self.db.delete(db_model)
        await self.db.commit()

    async def insert(
        self,
        model_obj: ModelT,
        commit: bool = True,
        refresh: bool = False,
    ) -> None:
        """
        inserts a model into the database

        Arguments:
            model_obj {ModelT} -- the model to be inserted

        Keyword Arguments:
            commit {bool} -- whether to commit the transaction (default: {True})
            refresh {bool} -- whether to refresh the model after commit (default: {False})
        """
        self.db.add(model_obj)

        if not commit:
            return

        await self.db.commit()
        if refresh:
            await self.db.refresh(model_obj)

    async def get_by(
        self,
        predicate: Any,
        options: list | None = None,
    ) -> ModelT | None:
        """returns the first model from the ModelT table in the database based on the predicate
        passed

        Arguments:
            predicate {Any} -- the predicate to filter records by

        Keyword Arguments:
            options {Optional[List]} -- sqlalchemy options (default: {None})

        Returns:
            Optional[ModelT] -- the frist model that matches the predicate
        """
        query = select(self.model).filter(predicate)
        if options:
            for option in options:
                query = query.options(option)

        result = await self.db.execute(query)
        output = result.scalars().first()
        return output

    async def get_all(
        self,
        predicate: Any | None = None
    ) -> list[ModelT]:
        """returns all of the models from ModelT table in the database


        Returns:
            List[ModelT] -- list of all the models
        """

        stmnt = select(self.model)
        if predicate:
            stmnt = stmnt.where(predicate)
        result = await self.db.execute(stmnt)
        models = result.scalars().all()
        return list(models) if models else []

    async def exists(self, predicate: Any) -> bool:
        """returns True if a model exists in the ModelT table in the database

        Arguments:
            predicate {Any} -- the predicate to filter records by

        Returns:
            bool -- True if a model exists, False otherwise
        """
        query = (
            select(func.count())
            .select_from(self.model)
            .filter(predicate)
        )
        result = await self.db.execute(query)
        count = result.scalar_one()
        return count > 0

    async def get_limited(
        self,
        skip: int = 0,
        limit: int = 100,
        options: list | None = None,
    ) -> list[ModelT]:
        """returns a limited number of models from the ModelT table in the database

        Keyword Arguments:
            skip {int} -- the number of models to skip (default: {0})
            limit {int} -- the number of models to return (default: {100})
            options {Optional[List]} -- sqlalchemy options (default: {None})
        Returns:
            List[ModelT]
        """

        query = select(self.model).offset(skip).limit(limit)
        if options:
            for option in options:
                query = query.options(option)

        result = await self.db.execute(query)
        models = result.scalars().all()
        return list(models) if models else []

    async def create(self, obj_in: dict) -> ModelT:
        """creates a new model using the pydantic model schema

        Arguments:
            obj_in {dict} -- pydantic model schema (model_dump())

        Returns:
            ModelT -- the newly created model
        """
        db_model = self.model(**obj_in)
        await self.insert(db_model, commit=True, refresh=True)
        return db_model

    async def update(self, db_model: ModelT, obj_in: dict) -> ModelT:
        """updates a model using the 'obj_in' in dictionary derived from the pydantic model schema
        Arguments:
            db_model: the model to update
            obj_in: pydantic model schema (model_dump())
        Returns:
            the newly updated model
        """
        for field, value in obj_in.items():
            if hasattr(db_model, field):
                setattr(db_model, field, value)

        await self.db.commit()
        await self.db.refresh(db_model)
        return db_model

    async def size(self) -> int:
        """returns the total number of records in the ORMs table

        Returns:
            int -- the total number of records
        """
        query = select(func.count()).select_from(self.model)
        result = await self.db.execute(query)
        total: int = result.scalar_one()
        return total

    async def count_rows_by(self, query: Select) -> int:
        """counts the total number of records that will be returned in a given query

        Arguments:
            query: the query to count
        Returns:
            the query with the count function applied
        """
        count_query = query.with_only_columns(
            func.count(), maintain_column_froms=True
        ).order_by(None)
        result = await self.db.execute(count_query)
        total: int = result.scalar_one()
        return total

    async def execute_on_all(self, statement: Select) -> list[ModelT]:
        """executes a query statement and returns the results

        Arguments:
            statement: the query statement
        Returns:
            the results of the query
        """
        result = await self.db.execute(statement)
        return result.scalars().all()  # type: ignore

    async def execute(self, statement: Select) -> ModelT | None:
        """executes a query statement and returns the results

        Arguments:
            statement: the query statement
        Returns:
            the results of the query
        """
        result = await self.db.execute(statement)
        return result.scalars().first()
    
