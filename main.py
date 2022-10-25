import asyncio
import sqlalchemy as sa
import pandas

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import text

Base = declarative_base()


class Person(Base):
    __tablename__ = "person"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(30))
    age = sa.Column(sa.Integer)

    def __repr__(self):
        return f"Person(id={self.id}, name={self.name}, age={self.age})"


def prettyprint(result):
    dataframe = pandas.DataFrame(result.all(), columns=result.keys())
    markdown = dataframe.to_markdown()
    print("\n" + markdown + "\n")


async def check_postgres_version(session):
    result = await session.execute(text("select version()"))
    prettyprint(result)


async def check_postgres_schema(session):
    result = await session.execute(text("select pg_catalog.current_schema()"))
    prettyprint(result)


async def check_db_info(session):
    result = await session.execute(
        text(
            "select oid, datname, datconnlimit, dattablespace, datcollate, datctype, datcollversion"
            " from pg_catalog.pg_database"
            " where datname = 'postgres'"
        )
    )
    prettyprint(result)


async def check_db_size(session):
    result = await session.execute(text("select pg_catalog.pg_size_pretty(pg_database_size(current_database()))"))
    prettyprint(result)


async def check_db_config(session):
    result = await session.execute(text("select source, setting from pg_catalog.pg_settings where source != 'default'"))
    prettyprint(result)


async def check_tables(session):
    result = await session.execute(text("select * from pg_catalog.pg_tables where schemaname = 'public'"))
    prettyprint(result)


async def check_columns(session):
    result = await session.execute(
        text(
            "select column_name, ordinal_position, column_default, is_nullable, data_type, character_maximum_length,"
            " numeric_precision, is_updatable"
            " from information_schema.columns"
            " where table_name = 'person'"
        )
    )
    prettyprint(result)


async def postgres_env_check(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            await check_postgres_version(session)
            await check_postgres_schema(session)
            await check_db_info(session)
            await check_db_size(session)
            await check_db_config(session)
            await check_tables(session)
            await check_columns(session)


async def env_check(engine):
    if engine.name == "postgresql":
        await postgres_env_check(engine)
    else:
        print("Performing other database environment check")


async def init(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


async def create(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            statement = sa.insert(Person).values(
                [
                    {"name": "jack", "age": 22},
                    {"name": "eric", "age": 24},
                    {"name": "lucy", "age": 31},
                ]
            )
            await session.execute(statement)
            await session.commit()


async def read_and_print(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(sa.select(Person))
            print("    Result:")
            for person in result.scalars():
                print("        " + str(person))


async def update(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        await session.execute(sa.update(Person).values({"age": Person.age + 1}))
        await session.commit()


async def delete(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            await session.execute(sa.delete(Person))
            await session.commit()


async def main():
    engines = [
        create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/postgres", echo=True),
        create_async_engine("mysql+asyncmy://mysql:mysql@localhost:3306/mysql", echo=True),
    ]
    action_funcs = [
        env_check,
        # init,
        # read_and_print,
        # create,
        # read_and_print,
        # update,
        # read_and_print,
        # delete,
        # read_and_print,
    ]
    for engine in engines:
        for func in action_funcs:
            await func(engine=engine)


if __name__ == "__main__":
    asyncio.run(main())
