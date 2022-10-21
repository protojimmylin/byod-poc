from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, relationship


# The Models
Base = declarative_base()


class Person(Base):
    __tablename__ = "person"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    age = Column(Integer)
    emails = relationship("Email", back_populates="person", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Person(id={self.id}, name={self.name}, age={self.age}, emails={self.emails})"


class Email(Base):
    __tablename__ = "email"
    id = Column(Integer, primary_key=True)
    address = Column(String(60), nullable=False)
    person_id = Column(Integer, ForeignKey("person.id"), nullable=False)
    person = relationship("Person", back_populates="emails")

    def __repr__(self):
        return f"Email(id={self.id}, address={self.address})"


# Some actions
def init(engine):
    """Create all tables.

    It will check if the table exists first.
    """
    Base.metadata.create_all(engine, checkfirst=True)


def create_users(engine):
    with Session(engine) as session:
        instances = [
            Person(
                name="Brian",
                age=19,
                emails=[],
            ),
            Person(
                name="Mary",
                age=24,
                emails=[],
            ),
        ]
        session.add_all(instances)
        session.commit()


def create_users_with_emails(engine):
    with Session(engine) as session:
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
        session.commit()


def read_all(engine):
    with Session(engine) as session:
        users = session.query(Person).all()
        for user in users:
            print("   ", user)
        addresses = session.query(Email).all()
        for address in addresses:
            print("   ", address)
        print("")


def update_eric_age(engine):
    with Session(engine) as session:
        session.query(Person).filter_by(name="eric").update({'age': Person.age + 1})
        session.commit()


def delete_all(engine):
    with Session(engine) as session:
        session.query(Email).delete()
        session.query(Person).delete()
        session.commit()


def main():
    """Our Main

    Call action functions with different database engines as parameters.
    """
    engines = [
        create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"),
        create_engine("mysql+pymysql://mysql:mysql@localhost:3306/mysql"),
        # create_engine("mssql+pyodbc://sa:mssql_password@localhost:1433/msdb?driver=ODBC+Driver+18+for+SQL+Server"),
        # To be tested
    ]
    action_funcs = [
        init,
        read_all,
        create_users,
        read_all,
        delete_all,
        read_all,
        create_users_with_emails,
        read_all,
        update_eric_age,
        read_all,
        delete_all,
        read_all,
    ]

    for engine in engines:
        for func in action_funcs:
            print(f"`{func.__name__}`:")
            func(engine=engine)


if __name__ == "__main__":
    main()

# TODO:
# 1. Write the MSSQL part, too.
# 2. Make the ORM functions asynchronous.
# 3. Check the source code about `chat_message` table.
# 4. Try to make those queries work without joining others tables.
