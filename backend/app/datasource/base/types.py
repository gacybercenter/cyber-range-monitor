
from typing import Any, Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.controller import CRUDController

from ...core.mixins.datasource import DatasourceMixin

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

    
