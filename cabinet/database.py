import os
import duckdb
import uuid # Will be needed for UUID primary key, though not directly in table creation string

# Environment variable for MotherDuck token
MOTHERDUCK_TOKEN = os.environ.get('MOTHERDUCK_TOKEN')

def get_db_connection(group_name: str, user_name: str) -> duckdb.DuckDBPyConnection:
    """
    Establishes a DuckDB connection, either to MotherDuck or a local file,
    and ensures the necessary schema and table are created.

    Args:
        group_name: The name of the group (schema in MotherDuck, part of path for local).
        user_name: The name of the user (table name).

    Returns:
        A DuckDB connection object.
    """
    conn = None
    if MOTHERDUCK_TOKEN:
        # Connect to MotherDuck
        # The group_name is treated as the database name in MotherDuck
        connection_string = f'motherduck:{group_name}'
        # print(f"Connecting to MotherDuck with database: {group_name}") # Removed print
        conn = duckdb.connect(connection_string, md_token=MOTHERDUCK_TOKEN)
        # In MotherDuck, connecting to a database effectively creates it if it doesn't exist or uses it.
        # Explicitly creating the database (schema)
        conn.execute(f"CREATE DATABASE IF NOT EXISTS {group_name};")
        # Switch to the database context
        conn.execute(f"USE {group_name};")
        # print(f"Using MotherDuck database: {group_name}") # Removed print
    else:
        # Connect to a local DuckDB file
        database_dir = os.path.join("cabinet", "_data", group_name)
        os.makedirs(database_dir, exist_ok=True)
        database_path = os.path.join(database_dir, f"{user_name}.duckdb")
        # print(f"Connecting to local DuckDB file: {database_path}") # Removed print
        conn = duckdb.connect(database=database_path, read_only=False)
        # For local files, the schema is implicitly handled by the file structure.
        # The user_name will be the table name within this file.
        # print(f"Using local DuckDB file: {database_path}") # Removed print

    # Common table creation logic
    # The table name is user_name
    table_creation_query = f"""
    CREATE TABLE IF NOT EXISTS {user_name} (
        id UUID PRIMARY KEY,
        title VARCHAR,
        author VARCHAR,
        url VARCHAR,
        tags VARCHAR[],
        locations VARCHAR[],
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        markdown VARCHAR,
        properties JSON
    );
    """
    try:
        conn.execute(table_creation_query)
        # print(f"Table '{user_name}' ensured to exist in '{group_name if MOTHERDUCK_TOKEN else database_path}'.") # Removed print
    except Exception as e:
        # print(f"Error creating table {user_name}: {e}") # Removed print
        # If table creation fails, we might want to close the connection or raise the error
        if conn:
            conn.close()
        raise

    return conn

if __name__ == '__main__':
    # Example usage for local DB
    print("Testing local database connection...")
    local_conn = None
    try:
        local_conn = get_db_connection("my_group", "test_user")
        print("Local connection successful. Table 'test_user' should exist in 'cabinet/_data/my_group/test_user.duckdb'")
        # You can add a simple query to test, e.g., local_conn.execute("SELECT COUNT(*) FROM test_user;").fetchone()
    except Exception as e:
        print(f"Local connection test failed: {e}")
    finally:
        if local_conn:
            local_conn.close()
    print("-" * 30)

    # Example usage for MotherDuck (requires MOTHERDUCK_TOKEN to be set)
    if MOTHERDUCK_TOKEN:
        print("Testing MotherDuck connection...")
        md_conn = None
        try:
            # Using a different group/user name for testing to avoid conflicts if needed
            md_conn = get_db_connection("my_cloud_group", "test_cloud_user")
            print("MotherDuck connection successful. Database 'my_cloud_group' and table 'test_cloud_user' should exist.")
            # Example: md_conn.execute("SELECT COUNT(*) FROM test_cloud_user;").fetchone()
        except Exception as e:
            print(f"MotherDuck connection test failed: {e}")
        finally:
            if md_conn:
                md_conn.close()
    else:
        print("MOTHERDUCK_TOKEN not set, skipping MotherDuck connection test.")

    # Test case: verify directory creation
    print("-" * 30)
    print("Testing directory creation...")
    if os.path.exists("cabinet/_data/my_group"):
        print("Directory 'cabinet/_data/my_group' was created successfully (or already existed).")
    else:
        print("ERROR: Directory 'cabinet/_data/my_group' was NOT created.")

    # Test case: check if local db file is created (will be empty if no data inserted)
    if os.path.exists("cabinet/_data/my_group/test_user.duckdb"):
        print("Local DB file 'cabinet/_data/my_group/test_user.duckdb' was created successfully (or already existed).")
    else:
        print("ERROR: Local DB file 'cabinet/_data/my_group/test_user.duckdb' was NOT created.")

    # Test with some actual data insertion and retrieval for local
    print("-" * 30)
    print("Testing local database with data insertion and retrieval...")
    local_conn_data_test = None
    try:
        local_conn_data_test = get_db_connection("data_test_group", "data_test_user")
        test_uuid = uuid.uuid4()
        local_conn_data_test.execute(f"INSERT INTO data_test_user (id, title, created_at) VALUES ('{test_uuid}', 'Test Title', NOW());")
        result = local_conn_data_test.execute(f"SELECT title FROM data_test_user WHERE id = '{test_uuid}';").fetchone()
        if result and result[0] == 'Test Title':
            print("Local data insertion and retrieval test successful.")
        else:
            print(f"ERROR: Local data insertion/retrieval test failed. Result: {result}")
        # Clean up test data
        local_conn_data_test.execute("DELETE FROM data_test_user;")
    except Exception as e:
        print(f"Local data test failed: {e}")
    finally:
        if local_conn_data_test:
            local_conn_data_test.close()

    print("-" * 30)
    print("Script finished.")
