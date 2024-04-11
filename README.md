# FastAPI Application

## Getting Started

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/VolskiyRoman/meduzzen-backend-internship
   
2. Navigate into the project directory:
    ```bash
   cd meduzzen-backend-internship
   
3. Create and activate a virtual environment
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    .\venv\Scripts\activate  # On Windows

4. Install the dependencies:
    ```bash
   pip install -r requirements.txt
   
5. Running the Application
   ```bash
   python main.py
   
## Alembic Migrations Guide

This guide will walk you through the process of creating and applying database migrations using Alembic, a popular migration tool for SQLAlchemy.

### What are Migrations?

Database migrations are scripts or files that allow you to manage changes to your database schema over time. They enable you to version-control your database schema changes, making it easier to deploy and maintain database structure across different environments (development, staging, production, etc.).

### Getting Started with Alembic

1. **Install Alembic**

   First, ensure you have SQLAlchemy and Alembic installed in your Python environment:
   ```bash
   pip install sqlalchemy alembic
   ```

2. **Initialize Alembic**

   Initialize Alembic in your project directory to set up the necessary directory structure and configuration files:
   ```bash
   alembic init alembic
   ```

   This command will create a directory named `alembic` containing configuration files (`alembic.ini`) and a `versions` directory where migration scripts will be stored.

3. **Define your SQLAlchemy Models**

   Create SQLAlchemy models that represent your database tables.

4. **Generate Migrations**

   Use Alembic to automatically generate an initial migration based on changes to your SQLAlchemy models:
   ```bash
   alembic revision --autogenerate -m "initial migration"
   ```

   This command will create a new migration script in the `versions` directory based on the differences between your current database schema and the models defined in `models.py`.

5. **Apply Migrations**

   Apply the generated migration to update your database schema:
   ```bash
   alembic upgrade head
   ```

   This command will execute the migration script and apply the necessary changes to your database schema.

6. **Creating Custom Migrations**

   For subsequent changes to your database schema, manually create new migration scripts using the `alembic revision` command:
   ```bash
   alembic revision -m "add column to users table"
   ```

   Then, edit the newly created migration script in `versions` directory to define the specific changes to be applied to the database schema.

7. **Apply Custom Migrations**

   Apply the custom migration to update your database schema:
   ```bash
   alembic upgrade head
   ```

### Additional Alembic Commands

- `alembic history`: View the revision history of applied migrations.
- `alembic downgrade <revision>`: Downgrade the database schema to a specific revision.
- `alembic current`: Show the current revision of the database.

For more information and advanced usage of Alembic, refer to the [Alembic documentation](https://alembic.sqlalchemy.org/en/latest/).

By following these steps, you can effectively manage database schema changes using Alembic migrations in conjunction with SQLAlchemy. This allows for seamless deployment and maintenance of database schemas in your projects.
