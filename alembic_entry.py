import pathlib

from dotenv import dotenv_values
from alembic.config import Config
from alembic import command

BASE_DIR = pathlib.Path(__file__).resolve().parent
ENV_VARS = dotenv_values(BASE_DIR / ".env")


def upgrade_to_head(url):
    config = Config(BASE_DIR / "alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")


def main():
    upgrade_to_head(url=ENV_VARS["POSTGRES_URL"])
    upgrade_to_head(url=ENV_VARS["MYSQL_URL"])


if __name__ == "__main__":
    main()
