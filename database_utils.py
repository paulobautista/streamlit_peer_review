import mysql.connector
from mysql.connector import Error as MySQLError
from typing import Optional
import uuid

def create_connection():
    return mysql.connector.connect(
        host='database-streamlit.czq8ik4asj60.ap-southeast-1.rds.amazonaws.com',
        user='admin',
        password='f*_anVhnyYFRK8veG',
        database='streamlit_ecliptor'
    )

def get_mysql_connection():
    """Get a new connection - should only be called once when starting the app"""
    return create_connection()

def get_total_review_documents():
    """Get the total count of peer review documents"""
    conn = get_mysql_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(DISTINCT review_index) FROM peer_review_documents')
        return cursor.fetchone()[0]
    finally:
        if cursor:
            cursor.close()
        conn.close()

def get_document_by_review_index(conn, review_index: int):
    """Get document information based on review_index from peer_review_documents"""
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        conn.ping(reconnect=True)

        query = """
        SELECT prd.*, d.markdown, d.image_path,
               aa.input_text as latest_edit,
               aa.user_decision
        FROM peer_review_documents prd
        JOIN documents d ON prd.document_id = d.id
        LEFT JOIN agent_actions aa ON prd.agent_action_id = aa.id
        WHERE prd.review_index = %s
        ORDER BY prd.created_at DESC
        LIMIT 1
        """

        cursor.execute(query, (review_index,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"Error fetching document: {str(e)}")
        return None
    finally:
        if cursor:
            cursor.close()

def insert_peer_review_action(conn, peer_review_document_id: str, reviewer_name: str, result: bool, comments: Optional[str] = None):
    """Insert a peer review action into the database"""
    cursor = None
    try:
        conn.ping(reconnect=True)
        cursor = conn.cursor()
        action_id = str(uuid.uuid4())

        query = """
        INSERT INTO peer_review_actions
        (id, peer_review_document_id, reviewer_name, result, comments)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (action_id, peer_review_document_id, reviewer_name, result, comments))
        conn.commit()
        return True
    except MySQLError as e:
        print(f"Error inserting peer review action: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
