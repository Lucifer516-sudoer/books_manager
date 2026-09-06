from shutil import rmtree

from config import settings


def uninstall_app_dir():
    rmtree(settings.APP_DIR)
