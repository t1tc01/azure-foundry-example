import logging
import struct

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import psycopg2

from backend.common.config import config

load_dotenv()
 
driver = config.ODBC_DRIVER
server = config.SQL_SERVER or "localhost"  # Fallback to localhost if empty
database = config.SQL_DATABASE
username = config.SQL_USERNAME
password = config.SQL_PASSWORD
mid_id = config.MID_ID

def dict_cursor(cursor):
    """
    Converts rows fetched by the cursor into a list of dictionaries.

    Args:
        cursor: A database cursor object.

    Returns:
        A list of dictionaries representing rows.
    """
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_connection():
    try:
        # Connect to PostgreSQL using explicit parameters to force TCP connection
        conn = psycopg2.connect(
            host=server,
            port=5432,
            database=database,
            user=username,
            password=password
        )
        logging.info("Connected to PostgreSQL database")
        return conn
    except psycopg2.Error as e:
        logging.error(f"Failed to connect to PostgreSQL: {str(e)}")
        return None

def get_invoice_name_from_db(invoice_id: str) -> str:
    conn = get_connection()
    if conn is None:
        return ""
    
    try:
        cursor = conn.cursor()
        sql = 'SELECT invoices."invoiceName" FROM invoices WHERE invoices.id = %s'
        cursor.execute(sql, (invoice_id,))
        row = cursor.fetchone()
        if row:
            return row[0] 
        else:
            return ""
    except Exception as e:
        logging.error(f"Error getting invoice name: {str(e)}")
        return ""
    finally:
        conn.close()

def get_invoice_update_history_from_db(invoice_id: str) -> str:
    conn = get_connection()
    if conn is None:
        return ""
    
    try:
        cursor = conn.cursor()
        sql = 'SELECT invoices."updateHistory" FROM invoices WHERE invoices.id = %s'
        cursor.execute(sql, (invoice_id,))
        row = cursor.fetchone()
        if row:
            return row[0] 
        else:
            return ""
    except Exception as e:
        logging.error(f"Error getting invoice update history: {str(e)}")
        return ""
    finally:
        conn.close()
