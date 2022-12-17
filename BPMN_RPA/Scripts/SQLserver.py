import re

import pyodbc
import pickle


# The BPMN-RPA SQLserver module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA SQLserver module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The BPMN-RPA SQLserver module is based on the pyodbc module (copyright Michael Kleehammer), which is licensed under the MIT license:
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


class SQLserver:

    def __init__(self, hostname, database, username="", password="", driver="{SQL Server Native Client 11.0}"):
        """
        Initializes the class and opens the database.
        :param hostname: The hostname of the SQL server
        :param database: Database name
        :param username: Optional. The username to use to connect to the server. If not specified, a trusted connection will be used.
        :param password: Optional. The password to use to connect to the server. If not specified, a trusted connection will be used.
        :param driver: Optional. The driver to use to connect to the server. If not specified, the SQL Server Native Client 11.0 driver will be used.
        """
        self.server = hostname
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.connection = None
        self.cursor = None
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect to the database.
        """
        if self.username != "" and self.password != "":
            self.connection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server + ';DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
        else:
            self.connection = pyodbc.connect('DRIVER=' + self.driver + ';SERVER=' + self.server + ';DATABASE=' + self.database + ';Trusted_Connection=yes;')
        self.cursor = self.connection.cursor()

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
        self.connection.close()
        return state

    def __setstate__(self, state):
        """
        Internal function for deserialization
        :param state: The state to set to the 'self' object of the class
        """
        self.__dict__.update(state)
        self.__connect__()

    def sqlserver_does_table_exist(self, table_name):
        """
        Checks if a table exists
        :param table_name: Name of the table
        :return: True if the table exists, false if not
        """
        return self.cursor.tables(table=table_name).fetchone() is not None

    def sqlserver_column_exist(self, table_name, column_name):
        """
        Checks if a column exists in a table
        :param table_name: Name of the table
        :param column_name: Name of the column
        :return: True if the column exists, false if not
        """
        return self.cursor.columns(table=table_name, column=column_name).fetchone() is not None

    def sqlserver_execute_query(self, query):
        """
        Executes a query against the database.
        :param query: The query to execute
        :return: The result of the query
        """
        return self.cursor.execute(query)

    def sqlserver_get_table_names(self):
        """
        Returns a list of all table names
        :return: List of table names
        """
        return self.cursor.tables()

    def sqlserver_get_table_columns(self, table_name):
        """
        Returns a list of all column names of a table
        :param table_name: Name of the table
        :return: List of column names
        """
        return self.cursor.columns(table=table_name)

    def sqlserver_get_table_data(self, table_name):
        """
        Returns a list of all data of a table
        :param table_name: Name of the table
        :return: List of data
        """
        return self.cursor.execute("SELECT * FROM " + table_name).fetchall()

    def sqlserver_get_table_data_by_column(self, table_name, column_name, column_value):
        """
        Returns a list of all data of a table by a column
        :param table_name: Name of the table
        :param column_name: Name of the column
        :param column_value: Value of the column
        :return: List of data
        """
        return self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + column_name + " = ?", column_value).fetchall()

    def sqlserver_get_table_data_by_columns(self, table_name, column_names, column_values):
        """
        Returns a list of all data of a table by multiple columns
        :param table_name: Name of the table
        :param column_names: List of column names
        :param column_values: List of column values
        :return: List of data
        """
        query = "SELECT * FROM " + table_name + " WHERE "
        for i in range(len(column_names)):
            if i > 0:
                query += " AND "
            query += column_names[i] + " = ?"
        return self.cursor.execute(query, column_values).fetchall()

    def sqlserver_get_table_data_by_columns_and_operator(self, table_name, column_names, column_values, operator):
        """
        Returns a list of all data of a table by multiple columns and an operator
        :param table_name: Name of the table
        :param column_names: List of column names
        :param column_values: List of column values
        :param operator: Operator to use (and or)
        :return: List of data
        """
        query = "SELECT * FROM " + table_name + " WHERE "
        for i in range(len(column_names)):
            if i > 0:
                query += " " + operator + " "
            query += column_names[i] + " = ?"
        return self.cursor.execute(query, column_values).fetchall()

    def sqlserver_execute_and_commit(self, query):
        """
        Executes a query against the database and commits the changes.
        :param query: The query to execute
        :return: The result
        """
        result = self.cursor.execute(query)
        self.connection.commit()
        return result

    def sqlserver_execute_and_commit_with_parameters(self, query, parameters):
        """
        Executes a query against the database and commits the changes.
        :param query: The query to execute
        :param parameters: The parameters to use
        :return: The result
        """
        result = self.cursor.execute(query, parameters)
        self.connection.commit()
        return result

    def sqlserver_escape_string(self, string: str, strip: bool=True) -> str:
        """
        Escape a string with single quotes for SQL-server use.
        :param string: The string to escape.
        :param strip: Optional. Strip the string before escaping. Default is True.
        :return: The escaped string.
        """
        if strip:
            string = string.strip()
        return string.replace(r"'", r"''")

    def sqlserver_query_and_get_results(self, query):
        """
        Executes a query against the database and returns the results.
        :param query: The query to execute
        :return: The results
        """
        return self.cursor.execute(query).fetchall()

    def sqlserver_close(self):
        """
        Closes the connection to the database
        """
        self.connection.close()

    def sqlserver_create_table(self, table_name, column_names, column_types):
        """
        Creates a table
        :param table_name: Name of the table
        :param column_names: List of column names
        :param column_types: List of column types
        """
        query = "IF NOT EXISTS (SELECT * FROM sys.tables t JOIN sys.schemas s ON (t.schema_id = s.schema_id) WHERE s.name = 'dbo' AND t.name = '" + table_name + "') CREATE TABLE " + table_name + " ("
        for i in range(len(column_names)):
            if i > 0:
                query += ", "
            query += column_names[i] + " " + column_types[i]
        query += ")"
        self.cursor.execute(query)
        self.connection.commit()

    def sqlserver_insert_into_table(self, table_name, column_names, column_values):
        """
        Inserts data into a table
        :param table_name: Name of the table
        :param column_names: List of column names
        :param column_values: List of column values
        """
        query = "INSERT INTO " + table_name + " ("
        for i in range(len(column_names)):
            if i > 0:
                query += ", "
            query += column_names[i]
        query += ") VALUES ("
        for i in range(len(column_names)):
            if i > 0:
                query += ", "
            query += "?"
        query += ")"
        self.cursor.execute(query, column_values)
        self.connection.commit()

    def sqlserver_update_table(self, table_name, column_names, column_values, where_column_names, where_column_values):
        """
        Updates data in a table
        :param table_name: Name of the table
        :param column_names: List of column names
        :param column_values: List of column values
        :param where_column_names: List of where column names
        :param where_column_values: List of where column values
        """
        query = "UPDATE " + table_name + " SET "
        for i in range(len(column_names)):
            if i > 0:
                query += ", "
            query += column_names[i] + " = ?"
        query += " WHERE "
        for i in range(len(where_column_names)):
            if i > 0:
                query += " AND "
            query += where_column_names[i] + " = ?"
        self.cursor.execute(query, column_values + where_column_values)
        self.connection.commit()

    def sqlserver_delete_from_table(self, table_name, where_column_names, where_column_values):
        """
        Deletes data from a table
        :param table_name: Name of the table
        :param where_column_names: List of where column names
        :param where_column_values: List of where column values
        """
        query = "DELETE FROM " + table_name + " WHERE "
        for i in range(len(where_column_names)):
            if i > 0:
                query += " AND "
            query += where_column_names[i] + " = ?"
        self.cursor.execute(query, where_column_values)
        self.connection.commit()

    def sqlserver_drop_table(self, table_name):
        """
        Drops a table
        :param table_name: Name of the table
        """
        self.cursor.execute("DROP TABLE " + table_name)
        self.connection.commit()

    def sqlserver_get_table_column_names(self, table_name):
        """
        Returns a list of all column names of a table
        :param table_name: Name of the table
        :return: List of column names
        """
        return [column[0] for column in self.cursor.execute("SELECT * FROM " + table_name).description]

    def sqlserver_get_table_column_types(self, table_name):
        """
        Returns a list of all column types of a table
        :param table_name: Name of the table
        :return: List of column types
        """
        return [column[1] for column in self.cursor.execute("SELECT * FROM " + table_name).description]

    def sqlserver_get_table_column_count(self, table_name):
        """
        Returns the number of columns of a table
        :param table_name: Name of the table
        :return: Number of columns
        """
        return len(self.cursor.execute("SELECT * FROM " + table_name).description)

    def sqlserver_get_table_count(self, table_name):
        """
        Returns the number of rows of a table
        :param table_name: Name of the table
        :return: Number of rows
        """
        return self.cursor.execute("SELECT COUNT(*) FROM " + table_name).fetchone()[0]

    def sqlserver_get_table_column_values(self, table_name, column_name):
        """
        Returns a list of all values of a column of a table
        :param table_name: Name of the table
        :param column_name: Name of the column
        :return: List of values
        """
        return [row[0] for row in self.cursor.execute("SELECT " + column_name + " FROM " + table_name).fetchall()]

    def sqlserver_get_table_column_value(self, table_name, column_name, where_column_names, where_column_values):
        """
        Returns the value of a column of a table
        :param table_name: Name of the table
        :param column_name: Name of the column
        :param where_column_names: List of where column names
        :param where_column_values: List of where column values
        :return: Value
        """
        query = "SELECT " + column_name + " FROM " + table_name + " WHERE "
        for i in range(len(where_column_names)):
            if i > 0:
                query += " AND "
            query += where_column_names[i] + " = ?"
        return self.cursor.execute(query, where_column_values).fetchone()[0]

    def sqlserver_get_table_column_values_where(self, table_name, column_name, where_column_names, where_column_values):
        """
        Returns a list of all values of a column of a table
        :param table_name: Name of the table
        :param column_name: Name of the column
        :param where_column_names: List of where column names
        :param where_column_values: List of where column values
        :return: List of values
        """
        query = "SELECT " + column_name + " FROM " + table_name + " WHERE "
        for i in range(len(where_column_names)):
            if i > 0:
                query += " AND "
            query += where_column_names[i] + " = ?"
        return [row[0] for row in self.cursor.execute(query, where_column_values).fetchall()]

    def sqlserver_clean_text_with_text_from_table(self, text, table_name, column_name):
        """
        Cleans a text with text from a table. It gets all the values of a column of a table and removes those values from the text.
        :param text: Text to clean
        :param table_name: Name of the table
        :param column_name: Name of the column
        :return: Cleaned text
        """
        for word in self.sqlserver_get_table_column_values(table_name, column_name):
            text = text.replace(word, "")
        return text
