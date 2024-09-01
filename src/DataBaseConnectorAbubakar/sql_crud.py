import sqlite3
from typing import Any, List, Dict, Tuple

class sql_operation:
    __connection = None  # Private variable
    
    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_connection(self) -> sqlite3.Connection:
        if sql_operation.__connection is None:
            sql_operation.__connection = sqlite3.connect(self.db_path)
        return sql_operation.__connection
    
    def execute_query(self, query: str, params: Tuple = ()) -> None:
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            cursor.close()

    def fetch_data(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        connection = self.create_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return data

    def insert_record(self, table: str, record: Dict[str, Any]) -> None:
        columns = ', '.join(record.keys())
        placeholders = ', '.join('?' * len(record))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, tuple(record.values()))

    def bulk_insert(self, table: str, records: List[Dict[str, Any]]) -> None:
        if not records:
            raise ValueError("No records provided for bulk insert.")
        columns = ', '.join(records[0].keys())
        placeholders = ', '.join('?' * len(records[0]))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            cursor.executemany(query, [tuple(record.values()) for record in records])
            connection.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            cursor.close()

    def update_record(self, table: str, update_values: Dict[str, Any], condition: str, condition_params: Tuple) -> None:
        set_clause = ', '.join([f"{key} = ?" for key in update_values.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        params = tuple(update_values.values()) + condition_params
        self.execute_query(query, params)

    def delete_record(self, table: str, condition: str, condition_params: Tuple) -> None:
        query = f"DELETE FROM {table} WHERE {condition}"
        self.execute_query(query, condition_params)

    def check_table_exists(self, table: str) -> bool:
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetch_data(query, (table,))
        return len(result) > 0

    def drop_table(self, table: str) -> None:
        if self.check_table_exists(table):
            self.execute_query(f"DROP TABLE {table}")
        else:
            print(f"Table '{table}' does not exist.")

    def close_connection(self) -> None:
        if sql_operation.__connection:
            sql_operation.__connection.close()
            sql_operation.__connection = None
