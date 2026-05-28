import sqlite3
import config

def get_connection():
    if not hasattr(config, "DB_PATH") or not config.DB_PATH:
        raise FileNotFoundError("DB_PATH не задан в config.py")
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    """Преобразует sqlite3.Row в dict, автоматически убирая пробелы в именах колонок"""
    if row is None: return {}
    return {k.strip(): v for k, v in zip(row.keys(), row)}
