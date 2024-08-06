import sqlite3



# Define the element you want to use as a condition
def db_search(model,dbpath):
    """
    The `db_search` function connects to an SQLite database, executes a query to retrieve a row based on
    a given model, extracts the values from the row, and returns the values.
    
    :param model: The `model` parameter is the value used to search for a specific row in the database
    table. In this case, it is used to search for a row in the `device_lists` table where the `MODEL`
    column matches the `model` value
    :return: The function `db_search` returns the values of `column2_value` and `column1_value`.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(dbpath)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    element_value = model

    # Execute the SQL query to retrieve the row based on the element
    cursor.execute('SELECT VENDOR, DEVICE_TYPE FROM device_lists WHERE MODEL = ?', (element_value,))

    # Fetch the result
    row = cursor.fetchone()

    conn.close()
    # Extract the values from the row
    if row is not None:
        column1_value = row[0]
        column2_value = row[1]
        
        # Do something with the values
        print(column1_value,column2_value)
    # Close the cursor and the database connection
        return column2_value,column1_value




