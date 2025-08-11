
from pydantic import Field

from app.common.yml_config import YAMLSettings

SECTION_NAME = "cors"


class CORSConfig(YAMLSettings):
    allow_origins: list[str] = Field(
        default=["*"], description="The allowed origins for CORS requests"
    )

    allow_methods: list[str] = Field(
        default=["*"], description="The allowed methods for CORS requests"
    )

    allow_headers: list[str] = Field(
        default=["*"],
        description="The allowed headers for CORS requests"
    )

    allow_credentials: bool = Field(
        True, description="Whether to allow credentials for CORS requests"
    )


cors_settings = CORSConfig.create(
    section_name=SECTION_NAME,
)
