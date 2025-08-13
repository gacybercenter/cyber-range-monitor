from typing import Annotated, Any, Type

from app.db.dependency import DatabaseDep
from api.openapi_extra import (
    APIResponses,
    ErrorDoc,
    UserAuthErrors,
    NotFound,
)

from app.common.schemas.http import MessagedResponse
from app.api.users.dependency import RoleRequired, UserRequired, AdminRequired

from fastapi import APIRouter, Body, Depends, Security, status

from app.common.types import PathID
from .base_schema import RouterAnnotations, ConnectionTestResults
from .source_service_abc import DatasourceServiceABC


def datasource_service_dep(service: Type[DatasourceServiceABC]):
    """returns the datasource service for the given datasource type

    Arguments:
        datasource_type {str} -- the datasource type to get the service for
        db {AsyncSession} -- the database session to use

    Returns:
        DatasourceServiceABC -- the datasource service for the given datasource type
    """

    async def service_dep(db: DatabaseDep) -> DatasourceServiceABC:
        return service(db=db)  # type: ignore

    return service_dep


def create_datasource_router(
    *, service: Type[DatasourceServiceABC], annotations: RouterAnnotations
) -> APIRouter:
    """Creates a router for the given datasource type with all of the
    shared routes, the prefix is added later in route registration

    Args:
        service (Type[DatasourceServiceABC]): _the service class_
        annotations (RouterAnnotations): _the type annotations for openapi_

    Returns:
        APIRouter: _the API Router_
    """
    router = APIRouter(
        dependencies=[Security(RoleRequired)],
        responses=UserAuthErrors(),
    )

    CreateBody = Annotated[annotations.CreateBody, Body(...)]
    UpdateBody = Annotated[annotations.UpdateBody, Body()]
    ServiceDepends = Depends(datasource_service_dep(service))

    @router.get(
        "/",
        response_model=annotations.ListResponse,
        status_code=status.HTTP_200_OK,
        description="Get all datasources",
    )
    async def read_all_datasources(
        service: DatasourceServiceABC = ServiceDepends,
    ):
        """Returns all of the datasources in the database of the given type

        Args:
            service (DatasourceServiceABC, optional):  Defaults to ServiceDepends.
        """
        return await service.get_datasource_list()

    @router.post(
        "/",
        response_model=annotations.Response,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Security(AdminRequired)],
        description="Create a new datasource",
    )
    async def create_datasource(
        datasource: CreateBody,  # type: ignore
        service: DatasourceServiceABC = ServiceDepends,
    ) -> Any:
        response = await service.create(datasource)
        return response

    @router.get(
        "/{datasource_id}/",
        response_model=annotations.Response,
        status_code=status.HTTP_200_OK,
        description="Get a datasource by ID",
        responses=NotFound("datasource"),
    )
    async def read_datasource_id(
        datasource_id: PathID,
        service: DatasourceServiceABC = ServiceDepends,
    ) -> Any:
        db_model = await service.models.get_by_id(datasource_id)
        return service.to_response(db_model)

    @router.patch(
        "/{datasource_id}/",
        response_model=annotations.Response,
        status_code=status.HTTP_200_OK,
        dependencies=[Security(AdminRequired)],
        description="Update a datasource by ID",
        responses=NotFound("datasource"),
    )
    async def update_datasource_id(
        datasource_id: PathID,
        req_body: UpdateBody,  # type: ignore
        service: DatasourceServiceABC = ServiceDepends,
    ) -> Any:
        response = await service.update_by_id(req_body, datasource_id)
        return response

    @router.delete(
        "/{datasource_id}/",
        status_code=status.HTTP_200_OK,
        response_model=MessagedResponse,
        dependencies=[Security(AdminRequired)],
        responses=NotFound("datasource"),
    )
    async def delete_datasource_id(
        datasource_id: PathID,
        service: DatasourceServiceABC = ServiceDepends,
    ) -> Any:
        await service.delete_by_id(datasource_id)
        return MessagedResponse(
            message=f"Datasource {datasource_id} deleted successfully",
            data={"datasource_id": datasource_id},
        )

    @router.get(
        "/connect",
        response_model=ConnectionTestResults,
        dependencies=[Security(UserRequired)],
        status_code=status.HTTP_200_OK,
        responses=NotFound("enabled datasource"),
        description="Attempts to connect to the enabled datasource",
    )
    async def test_active_connection(
        service: DatasourceServiceABC = ServiceDepends,
    ) -> ConnectionTestResults:
        if service.type == "saltstack":
            return ConnectionTestResults(
                message="Saltstack isnt implemented yet",
                success=False,
            )
        enabled_model = await service.require_enabled()
        msg, success = await service.test_connection(enabled_model)
        return ConnectionTestResults(
            success=success,
            message=msg or "Connection successful",
        )

    @router.get(
        "/connect/{datasource_id}",
        response_model=ConnectionTestResults,
        status_code=status.HTTP_200_OK,
        dependencies=[Security(UserRequired)],
        description="Attempts to connect to the datasource by ID",
        responses=NotFound("datasource"),
    )
    async def test_connection_id(
        datasource_id: PathID,
        service: DatasourceServiceABC = ServiceDepends,
    ) -> ConnectionTestResults:
        """Performs a connection test to a datasource by ID

        Args:
            datasource_id (PathID): _the ID of the datasource to tets_
            service (DatasourceServiceABC, optional):

        Returns:
            ConnectionTestResults: the results
        """

        if service.type == "saltstack":
            return ConnectionTestResults(
                message="Saltstack isnt implemented yet",
                success=False,
            )
        model = await service.models.get_by_id(datasource_id)
        msg, success = await service.test_connection(model)
        return ConnectionTestResults(
            success=success,
            message=msg or "Connection successful",
        )

    @router.post(
        "/toggle/{datasource_id}",
        response_model=annotations.Response,
        status_code=status.HTTP_200_OK,
        responses=APIResponses(
            [
                NotFound("datasource"),
                ErrorDoc("DatasourceToggleError", 400, title="Toggle Error"),
            ]
        ),
        dependencies=[Security(AdminRequired)],
    )
    async def toggle_datasource_id(
        datasource_id: PathID,
        service: DatasourceServiceABC = ServiceDepends,
    ) -> Any:
        """toggles the enabled state of the datasource by ID"""
        response = await service.toggle_by_id(datasource_id)
        return response

    return router
