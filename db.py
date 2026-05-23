import mysql.connector
from mysql.connector import Error

# ─────────────────────────────────────────
# 1. CONNECTION
# ─────────────────────────────────────────
def get_db_connection():
    """Returns a MySQL connection to corpus_forge."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",         
            password="",
            database="corpus_forge"
        )
        return connection
    except Error as e:
        print(f"[DB] Connection error: {e}")
        return None


# ─────────────────────────────────────────
# 2. INSERTION
# ─────────────────────────────────────────
def insert_uploaded_file(filename, file_type, file_size, raw_text, cleaned_text, word_count):
    """
    Inserts a file record into uploaded_files.
    Returns the new row's ID on success, None on failure.
    """
    connection = get_db_connection()
    if connection is None:
        return None

    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO uploaded_files
                (filename, file_type, file_size, raw_text, cleaned_text, word_count)
            VALUES
                (%s, %s, %s, %s, %s, %s)
        """
        values = (filename, file_type, file_size, raw_text, cleaned_text, word_count)
        cursor.execute(query, values)
        connection.commit()
        return cursor.lastrowid          # the new auto-increment ID
    except Error as e:
        print(f"[DB] Insert error: {e}")
        try:
            connection.rollback()
        except Exception:
            pass
        return None
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        try:
            connection.close()
        except Exception:
            pass