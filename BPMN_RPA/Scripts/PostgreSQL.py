import pickle

import psycopg2


# The BPMN-RPA PostgreSQL module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA PostgreSQL module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The BPMN-RPA SQLserver module is based on the psycopg2 module (copyright Federico Di Gregorio),
# which is licensed under the GNU Lesser General Public License (LGPL) version 3: https://www.gnu.org/licenses/lgpl-3.0.en.html

class PostgreSQL:

    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self.__connect__()

    def __connect__(self):
        """ Connect to the PostgreSQL database server """
        self.connection = psycopg2.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.database)
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

    def disconnect(self):
        """ Disconnect from the PostgreSQL database server """
        self.connection.close()

    def execute_fetch_one(self, sql):
        """
        Execute a SQL statement and return the first row of the result set
        :param sql: SQL statement
        """
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def execute_fetch_all(self, sql):
        """
        Execute a SQL statement and return all rows of the result set
        :param sql: SQL statement
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def execute_commit(self, sql):
        """
        Execute a SQL statement and commit the changes
        :param sql: SQL statement
        """
        self.cursor.execute(sql)
        self.connection.commit()

    def execute_many_commit(self, sql, data):
        """
        Execute a SQL statement and commit the changes
        :param sql: SQL statement
        :param data: data to be inserted
        """
        self.cursor.executemany(sql, data)
        self.connection.commit()

    def execute_script(self, filename):
        """
        Execute a SQL script file
        :param filename: SQL script file
        """
        with open(filename, 'r') as file:
            self.cursor.execute(file.read())
            self.connection.commit()

    def execute_script_from_string(self, sql):
        """
        Execute a SQL script from a string
        :param sql: SQL script
        """
        self.cursor.execute(sql)
        self.connection.commit()

    def execute_script_from_file(self, filename):
        """
        Execute a SQL script from a file
        :param filename: SQL script file
        """
        with open(filename, 'r') as file:
            self.cursor.execute(file.read())
        self.connection.commit()

    def create_table(self, table_name, columns):
        """
        Create a table in the PostgreSQL database
        :param table_name: name of the table
        :param columns: list of columns
        """
        sql = "CREATE TABLE IF NOT EXISTS " + table_name + " ("
        for column in columns:
            sql += column + ", "
        sql = sql[:-2] + ")"
        self.execute_commit(sql)

    def insert(self, table_name, columns, values):
        """
        Insert a row into a table in the PostgreSQL database
        :param table_name: name of the table
        :param columns: list of columns
        :param values: list of values
        """
        sql = "INSERT INTO " + table_name + " ("
        for column in columns:
            sql += column + ", "
        sql = sql[:-2] + ") VALUES ("
        for value in values:
            sql += "'" + value + "', "
        sql = sql[:-2] + ")"
        self.execute_commit(sql)

    def insert_many(self, table_name, columns, values):
        """
        Insert multiple rows into a table in the PostgreSQL database
        :param table_name: name of the table
        :param columns: list of columns
        :param values: list of values
        """
        sql = "INSERT INTO " + table_name + " ("
        for column in columns:
            sql += column + ", "
        sql = sql[:-2] + ") VALUES ("
        for value in values:
            sql += "%s, "
        sql = sql[:-2] + ")"
        self.execute_many_commit(sql, values)

    def select(self, table_name, columns, where):
        """
        Select rows from a table in the PostgreSQL database
        :param table_name: name of the table
        :param columns: list of columns
        :param where: where clause
        """
        sql = "SELECT "
        for column in columns:
            sql += column + ", "
        sql = sql[:-2] + " FROM " + table_name + " WHERE " + where
        return self.execute_fetch_all(sql)

    def select_all(self, table_name, columns):
        """
        Select all rows from a table in the PostgreSQL database
        :param table_name: name of the table
        :param columns: list of columns
        """
        sql = "SELECT "
        for column in columns:
            sql += column + ", "
        sql = sql[:-2] + " FROM " + table_name
        return self.execute_fetch_all(sql)

    def update(self, table_name, columns, values, where):
        """
        Update rows in a table in the PostgreSQL database
        :param table_name: name of the table
        :param columns: list of columns
        :param values: list of values
        :param where: where clause
        """
        sql = "UPDATE " + table_name + " SET "
        for i in range(len(columns)):
            sql += columns[i] + " = '" + values[i] + "', "
        sql = sql[:-2] + " WHERE " + where
        self.execute_commit(sql)

    def delete(self, table_name, where):
        """
        Delete rows from a table in the PostgreSQL database
        :param table_name: name of the table
        :param where: where clause
        """
        sql = "DELETE FROM " + table_name + " WHERE " + where
        self.execute_commit(sql)

    def drop_table(self, table_name):
        """
        Drop a table in the PostgreSQL database
        :param table_name: name of the table
        """
        sql = "DROP TABLE " + table_name
        self.execute_commit(sql)

    def create_view(self, view_name, sql):
        """
        Create a view in the PostgreSQL database
        :param view_name: name of the view
        :param sql: SQL statement
        """
        self.execute_commit("CREATE VIEW " + view_name + " AS " + sql)

    def drop_view(self, view_name):
        """
        Drop a view in the PostgreSQL database
        :param view_name: name of the view
        """
        self.execute_commit("DROP VIEW " + view_name)

    def create_function(self, function_name, sql):
        """
        Create a function in the PostgreSQL database
        :param function_name: name of the function
        :param sql: SQL statement
        """
        self.execute_commit("CREATE FUNCTION " + function_name + " AS " + sql)

    def drop_function(self, function_name):
        """
        Drop a function in the PostgreSQL database
        :param function_name: name of the function
        """
        self.execute_commit("DROP FUNCTION " + function_name)

    def create_trigger(self, trigger_name, sql):
        """
        Create a trigger in the PostgreSQL database
        :param trigger_name: name of the trigger
        :param sql: SQL statement
        """
        self.execute_commit("CREATE TRIGGER " + trigger_name + " AS " + sql)

    def drop_trigger(self, trigger_name):
        """
        Drop a trigger in the PostgreSQL database
        :param trigger_name: name of the trigger
        """
        self.execute_commit("DROP TRIGGER " + trigger_name)

    def create_index(self, index_name, table_name, columns):
        """
        Create an index in the PostgreSQL database
        :param index_name: name of the index
        :param table_name: name of the table
        :param columns: list of columns
        """
        sql = "CREATE INDEX " + index_name + " ON " + table_name + " ("
        for column in columns:
            sql += column + ", "
        sql = sql[:-2] + ")"
        self.execute_commit(sql)

    def drop_index(self, index_name):
        """
        Drop an index in the PostgreSQL database
        :param index_name: name of the index
        """
        self.execute_commit("DROP INDEX " + index_name)

    def create_sequence(self, sequence_name):
        """
        Create a sequence in the PostgreSQL database
        :param sequence_name: name of the sequence
        """
        self.execute_commit("CREATE SEQUENCE " + sequence_name)

    def drop_sequence(self, sequence_name):
        """
        Drop a sequence in the PostgreSQL database
        :param sequence_name: name of the sequence
        """
        self.execute_commit("DROP SEQUENCE " + sequence_name)

    def create_schema(self, schema_name):
        """
        Create a schema in the PostgreSQL database
        :param schema_name: name of the schema
        """
        self.execute_commit("CREATE SCHEMA " + schema_name)

    def drop_schema(self, schema_name):
        """
        Drop a schema in the PostgreSQL database
        :param schema_name: name of the schema
        """
        self.execute_commit("DROP SCHEMA " + schema_name)

    def create_user(self, user_name, password):
        """
        Create a user in the PostgreSQL database
        :param user_name: name of the user
        :param password: password of the user
        """
        self.execute_commit("CREATE USER " + user_name + " WITH PASSWORD '" + password + "'")

    def drop_user(self, user_name):
        """
        Drop a user in the PostgreSQL database
        :param user_name: name of the user
        """
        self.execute_commit("DROP USER " + user_name)

    def create_role(self, role_name):
        """
        Create a role in the PostgreSQL database
        :param role_name: name of the role
        """
        self.execute_commit("CREATE ROLE " + role_name)

    def drop_role(self, role_name):
        """
        Drop a role in the PostgreSQL database
        :param role_name: name of the role
        """
        self.execute_commit("DROP ROLE " + role_name)

    def create_database(self, database_name):
        """
        Create a database in the PostgreSQL database
        :param database_name: name of the database
        """
        self.execute_commit("CREATE DATABASE " + database_name)

    def drop_database(self, database_name):
        """
        Drop a database in the PostgreSQL database
        :param database_name: name of the database
        """
        self.execute_commit("DROP DATABASE " + database_name)

    def create_tablespace(self, tablespace_name, location):
        """
        Create a tablespace in the PostgreSQL database
        :param tablespace_name: name of the tablespace
        :param location: location of the tablespace
        """
        self.execute_commit("CREATE TABLESPACE " + tablespace_name + " LOCATION '" + location + "'")

    def drop_tablespace(self, tablespace_name):
        """
        Drop a tablespace in the PostgreSQL database
        :param tablespace_name: name of the tablespace
        """
        self.execute_commit("DROP TABLESPACE " + tablespace_name)

    def create_language(self, language_name):
        """
        Create a language in the PostgreSQL database
        :param language_name: name of the language
        """
        self.execute_commit("CREATE LANGUAGE " + language_name)

    def drop_language(self, language_name):
        """
        Drop a language in the PostgreSQL database
        :param language_name: name of the language
        """
        self.execute_commit("DROP LANGUAGE " + language_name)

    def create_extension(self, extension_name):
        """
        Create an extension in the PostgreSQL database
        :param extension_name: name of the extension
        """
        self.execute_commit("CREATE EXTENSION " + extension_name)

    def drop_extension(self, extension_name):
        """
        Drop an extension in the PostgreSQL database
        :param extension_name: name of the extension
        """
        self.execute_commit("DROP EXTENSION " + extension_name)
