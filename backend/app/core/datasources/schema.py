from typing import Annotated, Generic, Literal

from pydantic import Field, ConfigDict


from typing import TypeVar

from app.core.schemas import APIRequestModel, CustomBaseModel, APIListResponse


DatasourceType = Literal['openstack', 'guacamole', 'saltstack']


class DatasourceOptions(APIRequestModel):
    pass


class DatasourceOptionsUpdate(APIRequestModel):
    '''The base update model for a datasource options'''
    pass


class DatasourceConnectionArgs(CustomBaseModel):
    '''Represents the arguments that when the model 
    is dumped can create a connection instance'''


OptionsT = TypeVar('OptionsT', bound=DatasourceOptions)
OptionsUpdateT = TypeVar('OptionsUpdateT', bound=DatasourceOptionsUpdate)


class DatasourceSchema(APIRequestModel):
    '''the base model for a datasource with all of the attributes present in each schema'''

    username: Annotated[str, Field(
        ..., description="The username for the datasource"
    )]
    endpoint: Annotated[str, Field(
        ..., description="The endpoint for the datasource"
    )]
    datasource_type: Annotated[DatasourceType, Field(
        ...,
        description="The type of the datasource used as a discriminator"
    )]

    def dump_no_discriminator(self) -> dict:
        '''serializes the model without the discriminator'''
        return self.model_dump(
            exclude={'datasource_type'},
            exclude_none=True,
            exclude_unset=True
        )


class DatasourceResponse(DatasourceSchema, Generic[OptionsT]):
    '''The datasource returned from the API
    Arguments:
        Generic {OptionsT} -- the model representing the options
        of the datasource
    '''
    id: Annotated[int, Field(..., description="The ID of the datasource")]

    options: Annotated[OptionsT, Field(
        ..., description="The options for the datasource"
    )]

    enabled: Annotated[bool, Field(
        ..., description="Whether the datasource is enabled"
    )]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra='ignore'
    )


ResponseT = TypeVar('ResponseT', bound=DatasourceResponse)


class DatasourceRequest(DatasourceSchema, Generic[OptionsT]):
    '''The base request model for a datasource
    Arguments:
        Generic {OptionsT} -- the model representing the options
        of the datasource
    '''
    password: Annotated[str, Field(
        ..., description="The password for the datasource"
    )]
    options: Annotated[OptionsT, Field(
        ..., description="The options for the datasource"
    )]


class DatasourceUpdate(DatasourceSchema, Generic[OptionsUpdateT]):
    '''The base update model for a datasource
    Arguments:
        Generic {OptionsT} -- the model representing the options
        of the datasource with them being optional
    '''
    username: Annotated[str | None, Field(
        None, description="The username for the datasource"
    )] = None
    password: Annotated[str | None, Field(
        None,
        description="The password for the datasource"
    )] = None
    endpoint: Annotated[str | None, Field(
        None,
        description="The endpoint for the Saltstack datasource"
    )] = None
    options: Annotated[OptionsUpdateT | None, Field(
        None,
        description="The options for the datasource"
    )] = None


class DatasourceListResponse(APIListResponse[ResponseT]):
    '''The response model for a list of datasources'''
    pass
