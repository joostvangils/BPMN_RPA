import pickle
import sqlite3

# The BPMN-RPA SqLite module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA SqLite module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


class SqLite:

    def __init__(self, database):
        """
        Opens a SQLite database and initializes the class for later use
        :param database: Path to the database
        """
        self.database = database
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect to the database
        """
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()

    def __is_picklable__(self, obj: any) -> bool:
        """
        Internal function to determine if the object is pickable.
        :param obj: The object to check.
        :return: True or False
        """
        try:
            pickle.dumps(obj)
            return True
        except Exception as e:
            return False

    def __getstate__(self):
        """
        Internal function for serialization
        """
        state = self.__dict__.copy()
        for key, val in state.items():
            if not self.__is_picklable__(val):
                state[key] = str(val)
        self.conn.close()
        return state

    def __setstate__(self, state):
        """
        Internal function for deserialization
        :param state: The state to set to the 'self' object of the class
        """
        self.__dict__.update(state)
        self.__connect__()

    def sqlite_does_table_exist(self, table_name):
        """
        Checks if a table exists
        :param table_name: Name of the table
        :return: True if the table exists
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='" + table_name + "'")
        return bool(self.cursor.fetchone())

    def sqlite_does_column_exist(self, table_name, column_name):
        """
        Checks if a column exists
        :param table_name: Name of the table
        :param column_name: Name of the column
        :return: True if the column exists
        """
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + column_name + " IS NOT NULL LIMIT 1")
        return bool(self.cursor.fetchone())

    def sqlite_add_column(self, table_name, column_name, column_type):
        """
        Adds a column to a table
        :param table_name: Name of the table
        :param column_name: Name of the column
        :param column_type: Type of the column
        """
        self.cursor.execute("ALTER TABLE " + table_name + " ADD COLUMN " + column_name + " " + column_type)
        self.conn.commit()

    def sqlite_add_row(self, table_name, column_names, column_values):
        """
        Adds a row to a table
        :param table_name: Name of the table
        :param column_names: List of column names
        :param column_values: List of column values
        """
        self.cursor.execute("INSERT INTO " + table_name + " (" + column_names + ") VALUES (" + column_values + ")")
        self.conn.commit()

    def sqlite_get_table_names(self):
        """
        Returns a list of all table names
        :return: List of table names
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return self.cursor.fetchall()

    def sqlite_get_table_columns(self, table_name):
        """
        Returns a list of all column names of a table
        :param table_name: Name of the table
        :return: List of column names
        """
        self.cursor.execute("PRAGMA table_info(" + table_name + ")")
        return self.cursor.fetchall()

    def sqlite_get_table_data(self, table_name):
        """
        Returns a list of all data of a table
        :param table_name: Name of the table
        :return: List of data
        """
        self.cursor.execute("SELECT * FROM " + table_name)
        return self.cursor.fetchall()

    def sqlite_get_table_data_by_column(self, table_name, column_name, column_value):
        """
        Returns a list of all data of a table by a column
        :param table_name: Name of the table
        :param column_name: Name of the column
        :param column_value: Value of the column
        :return: List of data
        """
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + column_name + " = '" + column_value + "'")
        return self.cursor.fetchall()

    def sqlite_get_table_data_by_column_like(self, table_name, column_name, column_value):
        """
        Returns a list of all data of a table by a column
        :param table_name: Name of the table
        :param column_name: Name of the column
        :param column_value: Value of the column
        :return: List of data
        """
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + column_name + " LIKE '%" + column_value + "%'")
        return self.cursor.fetchall()

    def sqlite_get_table_data_by_column_like_and(self, table_name, column_name, column_value, column_name2, column_value2):
        """
        Returns a list of all data of a table by a column
        :param table_name: Name of the table
        :param column_name: Name of the column
        :param column_value: Value of the column
        :return: List of data
        """
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + column_name + " LIKE '%" + column_value + "%' AND " + column_name2 + " LIKE '%" + column_value2 + "%'")
        return self.cursor.fetchall()

    def sqlite_get_table_data_by_column_like_or(self, table_name, column_name, column_value, column_name2, column_value2):
        """
        Returns a list of all data of a table by a column
        :param table_name: Name of the table
        :param column_name: Name of the column
        :param column_value: Value of the column
        :return: List of data
        """
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + column_name + " LIKE '%" + column_value + "%' OR " + column_name2 + " LIKE '%" + column_value2 + "%'")
        return self.cursor.fetchall()

    def sqlite_get_table_data_by_column_like_and_or(self, table_name, column_name, column_value, column_name2, column_value2, column_name3, column_value3):
        """
        Returns a list of all data of a table by a column
        :param table_name: Name of the table
        :param column_name: Name of the column
        :param column_value: Value of the column
        :return: List of data
        """
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + column_name + " LIKE '%" + column_value + "%' AND " + column_name2 + " LIKE '%" + column_value2 + "%' OR " + column_name3 + " LIKE '%" + column_value3 + "%'")
        return self.cursor.fetchall()

    def sqlite_create_table(self, table_name, columns):
        """
        Creates a table with the given columns
        :param table_name: Name of the table
        :param columns: List of columns
        """
        self.cursor.execute("CREATE TABLE " + table_name + " (" + ", ".join(columns) + ")")
        self.conn.commit()

    def sqlite_insert_table_data(self, table_name, columns, values):
        """
        Inserts data into a table
        :param table_name: Name of the table
        :param columns: List of columns
        :param values: List of values
        """
        self.cursor.execute("INSERT INTO " + table_name + " (" + ", ".join(columns) + ") VALUES (" + ", ".join(values) + ")")
        self.conn.commit()

    def sqlite_execute_and_commit(self, sql):
        """
        Executes a SQL statement
        :param sql: SQL statement
        """
        self.cursor.execute(sql)
        self.conn.commit()

    def sqlite_query_and_get_results(self, sql):
        """
        Executes a SQL statement and returns the results
        :param sql: SQL statement
        :return: List of results
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def sqlite_close(self):
        """
        Closes the connection to the database
        """
        self.conn.close()

    def sqlite_create_database(self, db_name):
        """
        Creates a database
        :param db_name: Name of the database
        """
        self.cursor.execute("CREATE DATABASE " + db_name)
        self.conn.commit()

    def sqlite_delete_database(self, db_name):
        """
        Deletes a database
        :param db_name: Name of the database
        """
        self.cursor.execute("DROP DATABASE " + db_name)
        self.conn.commit()

    def sqlite_get_all_databases(self):
        """
        Returns a list of all databases
        :return: List of databases
        """
        self.cursor.execute("SHOW DATABASES")
        return self.cursor.fetchall()

    def sqlite_get_all_tables(self):
        """
        Returns a list of all tables
        :return: List of tables
        """
        self.cursor.execute("SHOW TABLES")
        return self.cursor.fetchall()

    def sqlite_get_all_columns(self, table_name):
        """
        Returns a list of all columns of a table
        :param table_name: Name of the table
        :return: List of columns
        """
        self.cursor.execute("SHOW COLUMNS FROM " + table_name)
        return self.cursor.fetchall()

    def sqlite_get_all_column_names(self, table_name):
        """
        Returns a list of all column names of a table
        :param table_name: Name of the table
        :return: List of column names
        """
        self.cursor.execute("SHOW COLUMNS FROM " + table_name)
        return [column[0] for column in self.cursor.fetchall()]

    def sqlite_get_all_column_values(self, table_name, column_name):
        """
        Returns a list of all column values of a table
        :param table_name: Name of the table
        :param column_name: Name of the column
        :return: List of column values
        """
        self.cursor.execute("SELECT " + column_name + " FROM " + table_name)
        return [column[0] for column in self.cursor.fetchall()]

    def sqlite_get_all_column_values_with_condition(self, table_name, column_name, condition):
        """
        Returns a list of all column values of a table with a condition
        :param table_name: Name of the table
        :param column_name: Name of the column
        :param condition: Condition
        :return: List of column values
        """
        self.cursor.execute("SELECT " + column_name + " FROM " + table_name + " WHERE " + condition)
        return [column[0] for column in self.cursor.fetchall()]




