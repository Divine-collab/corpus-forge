try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:  # pragma: no cover - optional runtime dependency
    mysql = None

    class Error(Exception):
        pass

# ─────────────────────────────────────────
# 1. CONNECTION
# ─────────────────────────────────────────
def get_db_connection():
    """Returns a MySQL connection to corpus_forge."""
    if mysql is None:
        print("[DB] mysql-connector-python is not installed")
        return None

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


def insert_api_usage_log(document_id, query_text, input_tokens, output_tokens, total_tokens, created_at=None):
    """
    Inserts a Gemini API usage log row into api_usage_logs.
    Returns the new row's ID on success, None on failure.
    """
    connection = get_db_connection()
    if connection is None:
        return None

    cursor = None
    try:
        cursor = connection.cursor()
        if created_at is None:
            query = """
                INSERT INTO api_usage_logs
                    (document_id, query_text, input_tokens, output_tokens, total_tokens)
                VALUES
                    (%s, %s, %s, %s, %s)
            """
            values = (document_id, query_text, input_tokens, output_tokens, total_tokens)
        else:
            query = """
                INSERT INTO api_usage_logs
                    (document_id, query_text, input_tokens, output_tokens, total_tokens, created_at)
                VALUES
                    (%s, %s, %s, %s, %s, %s)
            """
            values = (document_id, query_text, input_tokens, output_tokens, total_tokens, created_at)

        cursor.execute(query, values)
        connection.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"[DB] API usage insert error: {e}")
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


def get_api_stats():
    """
    Fetch aggregate API usage statistics from api_usage_logs.
    Returns a dictionary with totals on success, or None on failure.
    """
    connection = get_db_connection()
    if connection is None:
        return None

    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            SELECT
                COUNT(*) AS total_api_requests,
                COALESCE(SUM(input_tokens), 0) AS total_input_tokens,
                COALESCE(SUM(output_tokens), 0) AS total_output_tokens,
                COALESCE(SUM(total_tokens), 0) AS total_tokens_overall
            FROM api_usage_logs
        """
        cursor.execute(query)
        result = cursor.fetchone()
        if not result:
            return {
                'total_api_requests': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_tokens_overall': 0,
            }

        return {
            'total_api_requests': int(result[0] or 0),
            'total_input_tokens': int(result[1] or 0),
            'total_output_tokens': int(result[2] or 0),
            'total_tokens_overall': int(result[3] or 0),
        }
    except Error as e:
        print(f"[DB] Stats retrieval error: {e}")
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


# ─────────────────────────────────────────
# 3. RETRIEVAL
# ─────────────────────────────────────────
def get_document_text(document_id):
    """
    Retrieve cleaned_text for a document by ID.
    Returns the cleaned_text string on success, None if not found or error.
    """
    connection = get_db_connection()
    if connection is None:
        return None
    
    cursor = None
    try:
        cursor = connection.cursor()
        query = "SELECT cleaned_text FROM uploaded_files WHERE id = %s"
        cursor.execute(query, (document_id,))
        
        result = cursor.fetchone()
        if result:
            return result[0]  # cleaned_text is the first column
        else:
            return None  # Document not found
    
    except Error as e:
        print(f"[DB] Retrieval error: {e}")
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


# ─────────────────────────────────────────
# 4. DELETION
# ─────────────────────────────────────────
def delete_uploaded_file(document_id):
    """
    Delete a file record from uploaded_files by ID.
    Returns True if a row was deleted, False otherwise.
    """
    connection = get_db_connection()
    if connection is None:
        return False

    cursor = None
    try:
        cursor = connection.cursor()
        query = "DELETE FROM uploaded_files WHERE id = %s"
        cursor.execute(query, (document_id,))
        connection.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"[DB] Delete error: {e}")
        try:
            connection.rollback()
        except Exception:
            pass
        return False
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