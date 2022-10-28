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

## Environment check

1. Postgres, MySQL, MSSQL all provide some kinds of version/schema information in there system tables.
2. There are also some special function like `version()` or `pg_database_size()` in postgres to be "called" using SQL.
3. Some of them even provide information about the OS. (like `version()` in postgres)
4. The way to get these information differ a lot among these databases. We may need to write it case by case.
5. SQLAlchemy also do some environment check things inside some of their function like `_get_server_version_info`.
6. If there are a existing testcases about these environment checks we can use it first and then improve it later.
7. Or we have to make sure what we want to know and check them one by one.
8. It is hard to make our client's DB work properly by this way.
9. Maybe we should still tell our clients BYOD is not 100% guranteed to work because they just own the DB, a part of our product.
10. We can still provide this kind of envrionment check as a basic precheck & diagnosis about client DB.
11. And when our backend goes wrong in the runtime because of our client's DB, we should still be ready to handle it in our backend's code.

## Flyway

1. Flyway uses Java as deps, but the backend code work with Flyway can be any other languages and calling Flyway's API through its command line interface.
2. Flyway itself provide a docker image too so we don't have to be worried about the Java deps part. We can just mount the migration files into Flyway's container and let it read it and connect to our client's DB to do the migrations.
3. About the migration files, Flyway works best with Java. You can write Jave code to do migration. like:

   ```
   package db.migration;

   import org.flywaydb.core.api.migration.BaseJavaMigration;
   import org.flywaydb.core.api.migration.Context;
   import java.sql.PreparedStatement;

   /**
   * Example of a Java-based migration.
   */
   public class V1_2__Another_user extends BaseJavaMigration {
       public void migrate(Context context) throws Exception {
           try (PreparedStatement statement =
                   context
                       .getConnection()
                       .prepareStatement("INSERT INTO test_user (name) VALUES ('Obelix')")) {
               statement.execute();
           }
       }
   }
   ```

4. But it provide SQL-based migration files, too. We can just write SQL file like:

   ```
   CREATE TABLE MyTable (
      MyColumn VARCHAR(100) NOT NULL
   );
   ```

   and mount it in Flyway's `/flyway/sql` and it will read it.

5. We want to create a empty DB ourself from the beginning so everything is recorded by Flyway, which is not a must but would be much easier to maintain.

6. We don't want our normal developers to be able to get the credentials about our client's databases. We don't want to use CI/CD things to do the migrations. We want to build a GUI interface and our clients should click a button themselves to trigger the migration.

7. Then, we need to trigger migration by Python programaticallu, which makes Flyway not a very good choice.

8. Maybe we can use SQLAlchemy or Django migration tools.

## Alembic

1. [Alembic](https://github.com/sqlalchemy/alembic) is a database migrations tool written by the author of SQLAlchemy.
2. Alembic uses a `.py` file to describe the migration and the table schema is written with `SQLAlchemy` like this:
   ```
   # 1975ea83b712_create_account_table.py
   def upgrade():
       op.create_table(
           'account',
           sa.Column('id', sa.Integer, primary_key=True),
           sa.Column('name', sa.String(50), nullable=False),
           sa.Column('description', sa.Unicode(200)),
       )

   def downgrade():
       op.drop_table('account')
   ```
3. Every migration files have two functions - `upgrade` and `downgrade` and some other information written in Python.
4. The migration file names start with some kind of UUID like a Git commit, and Alembic provides some commands to checkout to each version of the migrations. like:
   ```
   alembic upgrade head
   alembic upgrade 1975ea83b712
   alembic downgrade -1
   alembic upgrade 1975ea83b712+2
   ```
5. And other command like `alembic history` to check the history of the DB version.
6. Alembic provides many command-line APIs but we want to uses these functions with Python programmatically. 
7. And this should be easy because it seems that Alembic has a series of simple internal APIs written in Python and all the commands are just function calls. [Ref](https://alembic.sqlalchemy.org/en/latest/api/commands.html)

# TODOs:

1. Write the MSSQL part, too. (Done)
2. Find out how to do a environment check during our clients set up the database connection. (Doing)
3. Make the ORM functions asynchronous. (Done partially)
   (Ref: https://fastapi.tiangolo.com/advanced/async-sql-databases/, https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#synopsis-core)
4. Check the source code about `chat_message` table.
5. Try to make those queries work without joining others tables.
6. Do research how to handle mysql varchar and the posrgres's text fields.
