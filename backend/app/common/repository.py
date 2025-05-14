from typing import Any, Generic, TypeVar

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.selectable import Select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


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
        """deletes a model from the database
        Arguments:
            db_model {ModelT} -- the model to be deleted
        """
        await self.db.delete(db_model)
        await self.db.commit()

    async def save(self, model_obj: ModelT, refresh: bool = False) -> None:
        """saves a transaction to the database

        Args:
            model_obj (ModelT): _the model to save_
            refresh (bool, optional): _to refresh the model_. Defaults to False.
        """
        self.db.add(model_obj)
        await self.db.commit()
        if refresh:
            await self.db.refresh(model_obj)

    async def select(self, predicate: Any) -> ModelT | None:
        """returns the first model from the ModelT table in the database based on the predicate
        passed

        Arguments:
            predicate {Any} -- the predicate to filter records by

        Keyword Arguments:
            options {Optional[List]} -- sqlalchemy options (default: {None})

        Returns:
            Optional[ModelT] -- the frist model that matches the predicate
        """
        query = select(self.model).where(predicate)
        result = await self.db.execute(query)
        output = result.scalars().first()
        return output

    async def filter_by(self, **filters: Any) -> list[ModelT]:
        """returns a list of models from the ModelT table in the database based on the filters
        passed

        Arguments:
            filters {Any} -- the filters to filter records by

        Returns:
            List[ModelT] -- list of models that match the filters
        """
        query = select(self.model).filter_by(**filters)
        result = await self.db.execute(query)
        models = result.scalars().all()
        return list(models) if models else []

    async def select_all(self, predicate: Any | None = None) -> list[ModelT]:
        """returns all of the models from ModelT table in the database

        Returns:
            List[ModelT] -- list of all the models
        """
        stmnt = select(self.model)
        if predicate is not None:
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
        query = select(func.count()).select_from(self.model).filter(predicate)
        result = await self.db.execute(query)
        count = result.scalar_one()
        return count > 0

    async def select_limited(self, skip: int = 0, limit: int = 100) -> list[ModelT]:
        """returns a limited number of models from the ModelT table in the database

        Keyword Arguments:
            skip {int} -- the number of models to skip (default: {0})
            limit {int} -- the number of models to return (default: {100})
            options {Optional[List]} -- sqlalchemy options (default: {None})
        Returns:
            List[ModelT]
        """

        query = select(self.model).offset(skip).limit(limit)
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
        await self.save(db_model, refresh=True)
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

    async def count_by(self, query: Select) -> int:
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
