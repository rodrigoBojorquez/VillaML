from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",                 # <-- quitar "APP_"
        env_nested_delimiter="__"
    )

    environment:     str = "development"
    database_url:    str = "sqlite:///./app.db"
    raw_data_path:   str = "app/infrastructure/data/raw/raw_data.xlsx"
    models_dir:      str = "app/infrastructure/data/models"
