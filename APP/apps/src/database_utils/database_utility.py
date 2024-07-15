import os
import django
from django.db import connections
from contextlib import contextmanager
import pandas as pd

from dotenv import load_dotenv

load_dotenv()

# Ensure settings are properly configured
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'APP.django_setup.settings')
django.setup()

class DatabaseUtility:
    def __init__(self, alias='default'):
        """
        Initialize the utility with the option to specify the database alias.
        """
        self.alias = alias

    @property
    def connection(self):
        """
        Property to get the Django database connection.
        """
        return connections[self.alias]

    @contextmanager
    def get_cursor(self):
        """
        A context manager that lazily gets a cursor. Ensures the connection is closed after use.
        """
        cursor = None
        try:
            connection = self.connection
            cursor = connection.cursor()
            yield cursor
        except Exception as e:
            print(f"Database operation failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def execute_query(self, query, params=None, return_type='df'):
        """
        Execute a select query and return all rows.
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or [])
                if return_type == 'df':
                    df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])
                    return df
                else:
                    return cursor.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame() if return_type == 'df' else []

    def execute_query_dict(self, query, params=None):
        """
        Execute a select query and return all rows as a list of dictionaries.
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params or [])
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error executing query_dict: {e}")
            return []

# Usage example (ensure Django settings are configured):
# db_util = DatabaseUtility()
# df = db_util.execute_query("SELECT * FROM my_table WHERE some_column = %s", [some_value])
