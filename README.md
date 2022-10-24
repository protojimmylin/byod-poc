# byod-poc

A POC about bring-your-own-database.

## Quickstart

1. Git clone & CD into repo

   ```
   git clone https://github.com/protojimmylin/byod-poc
   cd byod-poc
   ```

2. Launch Databases

   ```
   docker-compose up
   ```

3. Install Python Deps

   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run the Python script

   See `main.py` for more detail.

   ```
   python main.py
   ```

5. Clean up

   Do it only when you want to clean all databases data/config.

   ```
   docker-compose prune
   ```

## Issues

1. Create tables by these codes will succeed with Postgres but fail MySQL:

   ```
   users = Table(
       "users",
       metadata,
       Column("id", Integer, primary_key=True),
       Column("name", String),
       Column("fullname", String),
   )
   ```

   MySQL would says:

   ```
   sqlalchemy.exc.CompileError: (in table 'users', column 'name'): VARCHAR requires a length on dialect mysql
   ```

2. `metadata.drop_all` may be stuck because of constraint things. Drop table with SQL statement including CASCADE keyword may work but then we need to write more raw SQL.

## Thoughts

1. Creating tables and droping tables are not something we will do very frequently, and the SQL statement is very static so we can just write raw SQL with every kinds of databases.
2. We only use BYOD solution in some tables. So maybe we can write a series of tests to make sure all the operations we do with ORM will work with Postgres/MySQL/MSSQL and so on.

## Other issues

1. Ubuntu need to install MSSQL driver to connect to MSSQL. ([Ref](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15#ubuntu18))
2. The bash script can't be executed directly. I ended up copy-paste these lines manually:

   ```
   sudo su
   curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

   curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list

   sudo apt-get update
   sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
   sudo ACCEPT_EULA=Y apt-get install -y mssql-tools18
   source ~/.bashrc
   sudo apt-get install -y unixodbc-dev
   ```

3. After installing the driver, there is still a certificate thing. I've not figuered this out yet:

   ```
   sqlalchemy.exc.OperationalError: (pyodbc.OperationalError) ('08001', '[08001] [unixODBC][Microsoft][ODBC Driver 18 for SQL Server]SSL Provider: [error:0A000086:SSL routines::certificate verify failed:self-signed certificate] (-1) (SQLDriverConnect)')
   (Background on this error at: https://sqlalche.me/e/14/e3q8)
   ```

4. It seems that MSSQL docker image doesn't provide a way to set up a initial DB. I might need to set it up with a script. ([Ref](https://github.com/microsoft/mssql-docker/issues/2))

5. `3.` may be solved by adding `TrustServerCertificate=yes` parameter in the connection string.

6. `4.` may be worked around by using the default `msdb` or `tempdb` database.

## Async ORM
1. Async ORM need async driver, or this error happens:
   ```
   sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async
   ```
2. Some database like MSSQL may not have a asynchronous driver, we can still use something like `conn.run_sync(...)` though.
3. SQLAlchemy's API is a little messy and some naming things are wierd.
   (Core/ORM API and many legacy, different syntax that is not compatible with each others.)
   (sessionmaker() return a session factory?)
4. Calling a model's `__repr__` in a asynchronous block will fail if the `__repr__` includes a field defined with `Relation(...)`.
5. Delete/Update syntax seems not same as the original synchronous ones.
6. FastAPI's documentation seems good and we are going to use it with SQLAlchemy. Maybe I should use it more.


# TODOs:
1. Write the MSSQL part, too. (Done)
2. Make the ORM functions asynchronous. (Doing)
   (Ref: https://fastapi.tiangolo.com/advanced/async-sql-databases/, https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#synopsis-core)
3. Check the source code about `chat_message` table.
4. Try to make those queries work without joining others tables.
5. Find out how to do a environment check during clients set up the database connection.
