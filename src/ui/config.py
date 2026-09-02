import json
from pathlib import Path

from platformdirs import user_applications_path
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    AUTHOR: str = "Lucifer516_sudoer"
    VERSION: str = "v0.0.1-alpha"
    APP_NANE: str = "BookManager"

    @property
    def app_dir(self) -> Path:
        return user_applications_path(
            self.APP_NANE, self.APP_NANE, self.VERSION, ensure_exists=True
        )

    @property
    def books_folder(self) -> Path:
        return self.app_dir / "Books"

    @property
    def configs_folder(self) -> Path:
        return self.app_dir / "Config"

    def as_json(self, file: Path | None = None) -> str:
        if issubclass(type(file), Path) and file:
            if file.is_file() and file.exists():
                with open(file.resolve().absolute(), "w+") as f:
                    json.dump(
                        self.model_dump(),
                        f,
                        indent=4,
                    )
                    return self.model_dump_json()
        return self.model_dump_json()


settings = Config()
