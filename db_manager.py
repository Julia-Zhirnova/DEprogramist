import sqlite3
import config

def get_connection():
    """Возвращает новое безопасное соединение с БД."""
    conn = sqlite3.connect(config.DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    """Безопасно преобразует sqlite3.Row в dict, убирая пробелы в ключах."""
    if row is None: return {}
    return {k.strip(): v for k, v in zip(row.keys(), row)}
