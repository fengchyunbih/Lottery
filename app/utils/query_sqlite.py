import sqlite3
from typing import List, Dict, Any

# SQLite database path
DB_PATH = 'app/instance/lottery.sqlite'

def query_sqlite(sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """
    Execute a SQL query and return the results as a list of dictionaries
    
    Args:
        sql (str): SQL query string
        params (tuple): Query parameters (optional)
        
    Returns:
        List[Dict[str, Any]]: Query results as a list of dictionaries
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Set row_factory to return results as dictionaries
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Execute query with parameters
            cursor.execute(sql, params)
            
            # Fetch all results and convert to list of dictionaries
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []
    
def insert_sqlite(sql: str, params: tuple = ()) -> int | None:
    """
    Execute a SQL insert statement
    
    Args:
        sql (str): SQL insert statement
        params (tuple): Query parameters (optional)
        
    Returns:
        int | None: Last row id if successful, None if error occurred
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        print(f"SQL statement: {sql}")
        print(f"Parameters: {params}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        print(f"SQL statement: {sql}")
        print(f"Parameters: {params}")
        return None