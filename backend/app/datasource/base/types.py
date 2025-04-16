
from typing import Any, Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.controller import CRUDController

from .model import DatasourceMixin

from .schema import (
    DatasourceReadModel,
    DatasourceUpdateModel,
    DatasourceCreateModel,
    DatasourceConnectionModel
)


DSMixin = TypeVar('DSMixin', bound=DatasourceMixin)
ReadMixin = TypeVar('ReadMixin', bound=DatasourceReadModel)
UpdateMixin = TypeVar('UpdateMixin', bound=DatasourceUpdateModel)
CreateMixin = TypeVar('CreateMixin', bound=DatasourceCreateModel)


class DatasourceServiceABC(
    CRUDController[DSMixin], Generic[DSMixin, ReadMixin]
):
    '''Outlines the methods that a datasource service
    can implement seperated from the controller class
    for readability.

    Arguments / Generics:
        - DatasourceT: The Database model for the datasource (must still set self.model in constructor)
        - DatasourceReadT: the response schema of the model
    '''

    def __init__(self, db: AsyncSession, model: Type[DSMixin]) -> None:
        self.db = db
        self.model: Type[DSMixin] = model

    # ==== Optional override(s) ====

    def _validate_schema(self, request_schema: DatasourceCreateModel) -> dict:
        '''Validates the request schema and serializes it into a dictionary
        by default, it simply serializes the schema. This is called in the
        create_datasource method which can be used to check the schema before
        the model is created in the databse.

        Arguments:
            request_schema {CustomBaseModel} -- the request schema

        Returns:
            dict -- the serialized schema
        '''
        return request_schema.serialize()

    # NOTE: ** must implement  **

    def serialize(self, source: DSMixin) -> ReadMixin:
        '''Serializes the datasource model into a DatasourceConnectionModel
        Arguments:
            source {DatasourceMixin} -- the datasource model

        Returns:
            DatasourceConnectionModel -- the serialized model
        '''
        raise NotImplementedError()

    async def connect_args(self, source: DSMixin) -> DatasourceConnectionModel:
        '''Converts a datasource model into a Pydantic Schema 
        for which when serialized represents a dictionary of 
        the arguments to create a connection instance

        Arguments:
            source {DatasourceMixin} -- the datasource model

        Returns:
            Any -- The connection arguments
        '''
        raise NotImplementedError()

    async def connect(self, source: DSMixin) -> Any:
        '''Creates a connection instance from a datasource model
        Arguments:
            source {DatasourceMixin} -- the datasource model

        Returns:
            Any -- The connection instance
        '''
        raise NotImplementedError()

    async def test_datasource_connection(self, source: DSMixin) -> tuple[str | None, bool]:
        '''Tests the connection to the datasource

        Arguments:
            source {DatasourceMixin} -- the datasource model

        Returns:
            tuple[str, bool] -- the connection status
        '''
        raise NotImplementedError()
