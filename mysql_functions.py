#                   _____    _____.___.             _________ ________    .____      
#                  /     \   \__  |   |            /   _____/ \_____  \   |    |     
#                 /  \ /  \   /   |   |   ______   \_____  \   /  / \  \  |    |     
#                /    Y    \  \____   |  /_____/   /        \ /   \_/.  \ |    |___  
#                \____|__  /  / ______|           /_______  / \_____\ \_/ |_______ \ 
#                        \/   \/                          \/         \__>         \/ 
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------


#   Project         :   Insurance-AI
#   File            :   mysql_functions.py
#   Programmers     :   Alonzo Gutierrez, Sebastian Posada
#   Description     :   This module provides functions for interacting with a MySQL database.
#                       It includes functions to establish a database connection and insert email information into the database.
#                       The database configuration is specified in the 'db_config' dictionary.

#   First Version   :   September 8, 2023


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import mysql.connector


# Database Configuration
# ----------------------
# This dictionary stores the configuration parameters required to connect to the database.
# - "host": The hostname or IP address of the database server (e.g., "localhost").
# - "user": The username for authenticating with the database server.
# - "password": The password for authenticating with the database server.
# - "database": The name of the database to connect to (e.g., "document_db").
# ----------------------
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "crbQ#8xGTM",
    "database": "document_db"
}

def database_login():
    """
    Establishes a connection to a MySQL database and returns the connection object.

    Args:
        db_config (dict): A dictionary containing MySQL database connection parameters.

    Returns:
        mysql.connector.connection_cext.CMySQLConnection: A MySQL database connection object.
    """
    try:
        # Create connection to the database
        connection = mysql.connector.connect(**db_config)

        # Create a cursor to execute SQL queries
        print("Successfully logged in to MySQL database")
        return connection

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def insert_email_to_database(sender_address, receiver_address, body, cursor, connection):
    """
    Inserts email information into a database.

    Args:
        sender_address (str): The sender's email address.
        receiver_address (str): The receiver's email address.
        body (str): The email body content.
        cursor (mysql.connector.cursor_cext.CMySQLCursor): A MySQL database cursor.
        connection (mysql.connector.connection_cext.CMySQLConnection): A MySQL database connection.

    Returns:
        None
    """
    try:
        # Define the INSERT query
        insert_query = "INSERT INTO emails (sender_address, receiver_address, email_body) VALUES (%s, %s, %s)"
        data = (sender_address, receiver_address, body)

        # Execute the INSERT query
        cursor.execute(insert_query, data)

        # Commit changes (if any)
        connection.commit()

        print("Entry added to database")

    except Exception as e:
        print(f"An error occurred while inserting data: {str(e)}")

