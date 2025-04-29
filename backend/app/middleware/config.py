from typing import Annotated, List
from app.common.yml_settings import YMLBuildSettings, get_yml_file_section
from pydantic import Field



SECTION_NAME = 'cors'

class CORSConfig(YMLBuildSettings):

    allow_origins: Annotated[List[str], Field(
        '*',
        description="The allowed origins for CORS requests"
    )]

    allow_methods: Annotated[List[str], Field(
        '*',
        description="The allowed methods for CORS requests"
    )]

    allow_headers: Annotated[List[str], Field(
        '*',
        description="The allowed headers for CORS requests"
    )]

    allow_credentials: Annotated[bool, Field(
        True,
        description="Whether to allow credentials for CORS requests"
    )]
    


cors_settings = CORSConfig.load(
    get_yml_file_section(SECTION_NAME)
)
