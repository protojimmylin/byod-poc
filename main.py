import asyncio
import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Person(Base):
    __tablename__ = "person"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(30))
    age = sa.Column(sa.Integer)

    def __repr__(self):
        return f"Person(id={self.id}, name={self.name}, age={self.age})"


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
        init,
        read_and_print,
        create,
        read_and_print,
        update,
        read_and_print,
        delete,
        read_and_print,
    ]
    for engine in engines:
        for func in action_funcs:
            await func(engine=engine)


if __name__ == "__main__":
    asyncio.run(main())

# 1. Env check things.
# 2. https://docs.sqlalchemy.org/en/14/core/dml.html#sqlalchemy.sql.expression.Insert.values.
