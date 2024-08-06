import sqlite3


def create_table_and_insert_data(database_name, table_name, columns, data):
    """
    The function creates a table in an SQLite database and inserts data into the table.
    
    :param database_name: The name of the SQLite database file you want to connect to. This should
    include the file extension (.db)
    :param table_name: The table_name parameter is a string that specifies the name of the table you
    want to create in the SQLite database
    :param columns: The "columns" parameter is a list of strings that represents the column names of the
    table. Each string in the list should be the name of a column in the table
    :param data: The "data" parameter is a list of tuples, where each tuple represents a row of data to
    be inserted into the table. Each tuple should contain values corresponding to the columns specified
    in the "columns" parameter
    """

    # The function creates a table in an SQLite database and inserts data into the table.
    

    # Connect to the SQLite database
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Create a table
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
    cursor.execute(create_table_query)

    # Insert data into the table
    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])})"
    cursor.executemany(insert_query, data)
    print('inserted to the {}'.format(table_name))
    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

# Usage
# database_name = "your_database.db"
# table_name = "my_table"
# columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT", "name TEXT", "age INTEGER"]
# data = [
#     (1, "John", 25),
#     (2, "Alice", 30),
#     (3, "Bob", 35)
# ]
# create_table_and_insert_data(database_name, table_name, columns, data)
# print("Table created and data inserted successfully.") 


def fetch_last_row_column(column_name, table_name, database_name):

    # The function fetches the value of a specified column from the last row of a specified table in a
    # specified SQLite database.
    

    # Connect to the SQLite database
    conn = sqlite3.connect(database_name)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute the query to fetch the specified column of the last row
    try:
        query = f"SELECT {column_name} FROM {table_name} ORDER BY rowid DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
    

    # Close the cursor and database connection
        conn.commit()
        cursor.close()
        conn.close()

    # Access the fetched value
        if result:
            column_value = result[0]
            return column_value
    except :
        print("error")
        
# Example usage
# column_name = 'column_name'
# table_name = 'table_name'
# database_name = '/path/to/database.db'

# column_value = fetch_last_row_column(column_name, table_name, database_name)
# if column_value is not None:
#     print(f"Value of {column_name} in the last row: {column_value}")
# else:
#     print("No rows found in the table.")


def remove_row_by_value(table_name, column_name, value, database_name):
    
    # The function removes a row from a SQLite database table based on a specified value in a specified
    # column.
    
  
    # Connect to the SQLite database
    conn = sqlite3.connect(database_name)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute the query to remove the row with the specified value
    query = f"DELETE FROM {table_name} WHERE {column_name} = ?"
    cursor.execute(query, (value,))

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and database connection
    cursor.close()
    conn.close()

# Example usage
# table_name = 'table_name'
# column_name = 'column_name'
# value = 'desired_value'
# database_name = '/path/to/database.db'

# remove_row_by_value(table_name, column_name, value, database_name)



def search_index_column(table_name, index_column, database_name):
    """
    The `search_index_column` function retrieves the values of a specified index column from a table in
    an SQLite database.
    
    :param table_name: The name of the table in the SQLite database from which you want to retrieve the
    index column values
    :param index_column: The index_column parameter is the name of the column in the table from which
    you want to retrieve the values
    :param database_name: The name of the SQLite database file that you want to connect to
    :return: a list of values from the specified index column in the table.
    """
    
    # The function `search_index_column` retrieves the values of a specified index column from a table in
    # an SQLite database.
    


    # Connect to the SQLite database
    conn = sqlite3.connect(database_name)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute the query to fetch the index column value for each row
    query = f"SELECT {index_column} FROM {table_name}"
    cursor.execute(query)
    results = cursor.fetchall()

    # Close the cursor and database connection
    conn.commit()
    cursor.close()
    conn.close()

    # Return the index column values as a list
    return [result[0] for result in results]

# Example usage
# table_name = 'table_name'
# index_column = 'index_column'
# database_name = '/path/to/database.db'

# index_values = search_index_column(table_name, index_column, database_name)
# print("Index column values for each row:")
# for value in index_values:
#     print(value)

def search_column(tablename, databasename, columnname):

    # Connect to the SQLite database
    conn = sqlite3.connect(databasename)
    cursor = conn.cursor()

    # Retrieve the column data from the table
    cursor.execute(f"SELECT {columnname} FROM {tablename}")
    column_data = cursor.fetchall()

    # Extract the column values and store them in a list
    values_list = [row[0] for row in column_data]

    # Close the connection
    conn.close()

    # Return the list of column values
    return values_list



def find_highest_value(table_name, database_name, column_name):
    # Connect to the database
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Prepare the SQL query
    query = f"SELECT MAX({column_name}) FROM {table_name};"

    # Execute the query
    cursor.execute(query)

    # Fetch the result
    result = cursor.fetchone()[0]

    # Close the cursor and connection
    conn.commit()
    cursor.close()
    conn.close()

    # Return the highest value
    return result


def count_elements_in_column(table_name, database, column_name):
    # Establish a connection to the database
    conn = sqlite3.connect(database)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute the SQL query to count the elements in the column
    query = f"SELECT COUNT({column_name}) FROM {table_name}"
    cursor.execute(query)

    # Fetch the result of the query
    count = cursor.fetchone()[0]

    # Close the cursor and database connection
    cursor.close()
    conn.close()

    # Return the count of elements in the column
    return count


def add_column_and_populate_by_device_id(database_name, table_name, new_column_name, new_column_data, device_id):
    try:
        # Connect to the SQLite3 database
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()

        # Check if the new column already exists in the table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        if new_column_name in column_names:
            print(f"Column '{new_column_name}' already exists in table '{table_name}'.")
            return

        # Add a new column to the table
        add_column_query = f"ALTER TABLE {table_name} ADD COLUMN {new_column_name} TEXT"
        cursor.execute(add_column_query)

        # Populate the new column based on the input device_id
        populate_data_query = f"UPDATE {table_name} SET {new_column_name} = ? WHERE device_id = ?"
        cursor.execute(populate_data_query, (new_column_data, device_id))

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        print(f"Column '{new_column_name}' added and populated successfully in table '{table_name}'.")

    except sqlite3.Error as e:
        print(f"An exception occurred:{e}")

# Example usage:
# database_name = "your_database.db"
# table_name = "your_table"
# new_column_name = "new_column"
# new_column_data = "NewColumnDataForDeviceID123"  # Replace this with the data you want to add for the specific deviceid
# device_id = "123"  # Replace this with the deviceid for which you want to add the data

# add_column_and_populate_by_device_id(database_name, table_name, new_column_name, new_column_data, device_id)


def update_column_value(table_name, db_name, column_name, column_value, replace_value):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Fetch rows where the specified column has the given column_value
    cursor.execute(f"SELECT rowid, {column_name} FROM {table_name} WHERE {column_name} = ?", (column_value,))
    rows_to_update = cursor.fetchall()

    if rows_to_update:
        # Update the values in the specified column
        for row in rows_to_update:
            row_id, current_value = row
            new_value = current_value.replace(column_value, replace_value)
            cursor.execute(f"UPDATE {table_name} SET {column_name} = ? WHERE rowid = ?", (new_value, row_id))

        # Commit the changes to the database
        conn.commit()
        print(f"{len(rows_to_update)} row(s) updated successfully.")
    else:
        print("No matching rows found.")

    # Close the database connection
    conn.close()
   

# Example usage:
# Replace occurrences of 'old_value' with 'new_value' in 'column_name' of 'table_name'
# update_column_value('your_table_name', 'your_database.db', 'column_name', 'old_value', 'new_value')



def update_or_insert_row(database_name, table_name, columns, data):
    try:
        # Connect to the SQLite database
        with sqlite3.connect(database_name) as conn:
            cursor = conn.cursor()

            # Create a table if it does not exist
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            cursor.execute(create_table_query)

            # Delete the old row
            delete_query = f"DELETE FROM {table_name}"
            cursor.execute(delete_query)

            # Insert the new row
            insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])})"
            cursor.execute(insert_query, data)
            print(f'Updated row in the {table_name}')

            # Commit the changes to the database
            conn.commit()
            # conn.close()
  

        print(f'Committed changes to the database')
    except sqlite3.Error as e:
        print(f'An error occurred: {e}')
        print("error in grp database")

# # Example usage
# columns = ['id', 'name']
# data = (1, 'Alice')

# update_or_insert_row('mydatabase.db', 'mytable', columns, data)


# Example usage
# if __name__ == "__main__":
#     database_name = "my_database.db"
#     table_name = "my_table"
#     columns = ["id", "name", "age"]
#     data = [(1, "John", 30), (2, "Alice", 25), (3, "Bob", 28)]

#     create_table_and_replace_data(database_name, table_name, columns, data)



def retrieve_value(database_path, table_name, column1_name, column2_name, column1_value):
    # Connect to the SQLite database
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    try:
        # Execute the SQL query to retrieve the value from the second column
        query = f"SELECT {column2_name} FROM {table_name} WHERE {column1_name} = ?"
        cursor.execute(query, (column1_value,))
        
        # Fetch the result
        result = cursor.fetchone()

        if result:
            # If a matching row is found, return the value from the second column
            return result[0]
        else:
            # If no matching row is found, return a default value or handle it as needed
            return None

    finally:
        # Close the database connection
        connection.close()

# Example usage:
# database_path = "your_database.db"
# table_name = "your_table_name"
# column1_name = "column1"
# column2_name = "column2"
# column1_value_to_search = "desired_value"

# result_value = retrieve_value(database_path, table_name, column1_name, column2_name, column1_value_to_search)

# if result_value is not None:
#     print(f"The value in {column2_name} for {column1_name}={column1_value_to_search} is: {result_value}")
# else:
#     print(f"No matching row found for {column1_name}={column1_value_to_search}")

