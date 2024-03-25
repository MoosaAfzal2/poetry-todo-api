import secrets
import warnings
from typing import Annotated, Any, Literal, Union
from enum import Enum

from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class EnvironmentEnum(str, Enum):
    development = "development"
    production = "production"
    testing = "testing"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    PROJECT_NAME: str
    DESCRIPTION: str = "Todo API with FastAPI, SQLModel & Poetry"

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    VERSION: str = "1.0"
    API_STR: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 2  # 2 hours
    DOMAIN: str = "localhost"
    ENVIRONMENT: Union[EnvironmentEnum, str] = EnvironmentEnum.development

    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    @computed_field  # type: ignore[misc]
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    POSTGRES_DATABASE_URL: str

    # def _check_default_secret(self, var_name: str, value: str | None) -> None:
    #     if value == "changethis":
    #         message = (
    #             f'The value of {var_name} is "changethis", '
    #             "for security, please change it, at least for deployments."
    #         )
    #         if self.ENVIRONMENT == "local":
    #             warnings.warn(message, stacklevel=1)
    #         else:
    #             raise ValueError(message)

    # @model_validator(mode="after")
    # def _enforce_non_default_secrets(self) -> Self:
    #     self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
    #     self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
    #     self._check_default_secret(
    #         "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
    #     )

    #     return self


settings = Settings()  # type: ignore


class TestSettings(Settings):
    model_config = SettingsConfigDict(case_sensitive=True)
    ENVIRONMENT: Union[EnvironmentEnum, str] = EnvironmentEnum.testing
    TEST_USER_EMAIL : str
    TEST_USER_USERNAME : str
    TEST_USER_PASSWORD : str


test_settings = TestSettings()  # type: ignore
