import asyncio

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

# The Models
Base = declarative_base()


class Person(Base):
    __tablename__ = "person"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    age = Column(Integer)
    emails = relationship("Email", back_populates="person", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Person(id={self.id}, name={self.name}, age={self.age})"


class Email(Base):
    __tablename__ = "email"
    id = Column(Integer, primary_key=True)
    address = Column(String(60), nullable=False)
    person_id = Column(Integer, ForeignKey("person.id"), nullable=False)
    person = relationship("Person", back_populates="emails")

    def __repr__(self):
        return f"Email(id={self.id}, address={self.address})"


def update_eric_age(engine):
    with Session(engine) as session:
        session.query(Person).filter_by(name="eric").update({"age": Person.age + 1})
        session.commit()


async def init(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


async def create_users(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            instances = [
                Person(
                    name="jack",
                    age=22,
                    emails=[
                        Email(address="jack@google.com"),
                    ],
                ),
                Person(
                    name="eric",
                    age=24,
                    emails=[
                        Email(address="eric@google.com"),
                        Email(address="eric@yahoo.com"),
                    ],
                ),
                Person(
                    name="lucy",
                    age=31,
                    emails=[Email(address="lucy@yahoo.com")],
                ),
            ]
            session.add_all(instances)
            await session.commit()


async def create_users_with_emails(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            instances = [
                Person(
                    name="jack",
                    age=22,
                    emails=[
                        Email(address="jack@google.com"),
                    ],
                ),
                Person(
                    name="eric",
                    age=24,
                    emails=[
                        Email(address="eric@google.com"),
                        Email(address="eric@yahoo.com"),
                    ],
                ),
                Person(
                    name="lucy",
                    age=31,
                    emails=[Email(address="lucy@yahoo.com")],
                ),
            ]
            session.add_all(instances)
            await session.commit()


async def read_all(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            statement = select(Person)
            result = await session.execute(statement)
            for person in result.scalars():
                print("   ", person)
            statement = select(Email)
            result = await session.execute(statement)
            for email in result.scalars():
                print("   ", email)


# async def update_eric_age(engine):
#     with Session(engine) as session:
#         session.query(Person).filter_by(name="eric").update({"age": Person.age + 1})
#         session.commit()


async def delete_all(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        async with session.begin():
            statement = select(Person)
            result = await session.execute(statement)
            for person in result.scalars():
                session.delete(person)
            await session.commit()
    async with async_session() as session:
        async with session.begin():
            statement = select(Email)
            result = await session.execute(statement)
            for email in result.scalars():
                session.delete(email)
            await session.commit()


async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")
    action_funcs = [
        init,
        read_all,
        create_users,
        read_all,
        delete_all,
        read_all,
        create_users_with_emails,
        read_all,
        delete_all,
        read_all,
    ]
    for func in action_funcs:
        print(f"`{func.__name__}`:")
        await func(engine=engine)


if __name__ == "__main__":
    asyncio.run(main())
