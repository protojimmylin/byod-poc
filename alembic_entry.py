import pathlib

from alembic.config import Config
from alembic import command

BASE_DIR = pathlib.Path(__file__).resolve().parent
ALEMBIC_CONFIG = Config(BASE_DIR / "alembic.ini")


def upgrade(url, version):
    ALEMBIC_CONFIG.set_main_option("sqlalchemy.url", url)
    command.upgrade(ALEMBIC_CONFIG, version)


if __name__ == "__main__":
    upgrade("mysql+pymysql://root:Pa55w0rd!@localhost:3306/mysql", "head")
