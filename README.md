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
