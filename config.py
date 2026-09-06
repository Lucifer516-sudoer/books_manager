import json
from pathlib import Path

from platformdirs import user_data_path
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich import print


class AppSettings(BaseSettings):
    APP_NAME: str = "BooksManager"
    VERSION: str = "v0.0.1-alpha"
    AUTHOR: str = "Lucifer516-sudoer"

    @computed_field
    @property
    def APP_DIR(self) -> Path:
        return user_data_path(self.APP_NAME, version=self.VERSION, ensure_exists=True)

    @computed_field
    @property
    def LOGS_DIR(self) -> Path:
        return self.APP_DIR / "data" / "logs"

    @computed_field
    @property
    def DATABASE_DIR(self) -> Path:
        return self.APP_DIR / "data" / "database"

    @computed_field
    @property
    def CONFIG_FILE(self) -> Path:
        return self.APP_DIR / "config.json"

    @computed_field
    @property
    def DATABASE_FILE(self) -> Path:
        return self.DATABASE_DIR / "bookman.sqlite3"

    def write_to_json(self):
        try:
            with open(self.CONFIG_FILE, "w+") as file:
                json.dump(
                    self.model_dump,
                    file,
                    indent=4,
                )
                return True
        except Exception as err:
            # log the error
            print(err)
            return False

    def bootstrap(self) -> None:
        for each in [
            self.APP_DIR,
            self.DATABASE_DIR,
            self.LOGS_DIR,
        ]:
            if not each.exists():
                each.mkdir(parents=True, exist_ok=True)

        for each in [self.CONFIG_FILE]:
            if not each.exists():
                each.touch()

    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="ignore")

    @classmethod
    def load_settings(cls) -> "AppSettings":
        temp_settings = cls()
        config_path = temp_settings.CONFIG_FILE

        temp_settings.bootstrap()

        if config_path.exists() and config_path.stat().st_size > 0:
            try:
                with open(config_path, "r") as file:
                    file_data = json.load(file)
                    return cls(**file_data)
            except json.JSONDecodeError:
                pass

        return temp_settings


settings = AppSettings.load_settings()
