from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@property
def database_url(self) -> str:
    return (
        f"postgresql+asyncpg://"
        f"{self.postgres_user}:{self.postgres_password}"
        f"@{self.postgres_host}:{self.postgres_port}"
        f"/{self.postgres_db}"
    )


@property
def sync_database_url(self) -> str:
    return (
        f"postgresql+psycopg://"
        f"{self.postgres_user}:{self.postgres_password}"
        f"@{self.postgres_host}:{self.postgres_port}"
        f"/{self.postgres_db}"
    )


settings = Settings()