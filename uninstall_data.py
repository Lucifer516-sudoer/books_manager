from shutil import rmtree

import platformdirs
from rich import get_console
from rich.prompt import Confirm

from config import settings


def uninstall_app_dir():
    def prompt_the_dude(ith: int):
        return Confirm.ask(
            f"Do you {'really ' * (ith + 1)}wish to face the consequences?",
            default=False,
        )

    n = 3

    for i in range(n):
        response = prompt_the_dude(i)
        if response and i == n - 1:
            if not (
                settings.APP_DIR.parent.parent.resolve(strict=True)
                == platformdirs.user_data_path()
            ):
                get_console().print(
                    "Something is wrong, :sob: doing nothing."
                    "\nReally sorry :folded_hands:."
                )
                break
            else:
                rmtree(settings.APP_DIR)
                get_console().print(
                    ":relieved: Chillax... We've cleaned everything ...\nTats "
                    ":wave: ..."
                )
        if response is False:
            get_console().print(
                ":clapping_hands: Great choice [bold italic]dude[/] :+1:"
            )
            break


if __name__ == "__main__":
    uninstall_app_dir()
