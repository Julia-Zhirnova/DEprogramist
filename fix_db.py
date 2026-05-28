import sqlite3
import os

DB_FILE = "shoe_store.db"
if not os.path.exists(DB_FILE):
    print(f"❌ Файл {DB_FILE} не найден. Проверь, что ты в папке проекта.")
    exit()

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# 1. Чистим пробелы в именах таблиц
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '% ';")
for row in cur.fetchall():
    old_name = row[0]
    new_name = old_name.strip()
    print(f"📦 Таблица: '{old_name}' -> '{new_name}'")
    cur.execute(f'ALTER TABLE "{old_name}" RENAME TO "{new_name}";')

# 2. Чистим пробелы в именах колонок
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cur.fetchall()]
for tbl in tables:
    cur.execute(f'PRAGMA table_info("{tbl}");')
    for col in cur.fetchall():
        old_col = col[1]
        if old_col != old_col.strip():
            new_col = old_col.strip()
            print(f"  📝 Колонка в {tbl}: '{old_col}' -> '{new_col}'")
            try: cur.execute(f'ALTER TABLE "{tbl}" RENAME COLUMN "{old_col}" TO "{new_col}";')
            except Exception as e: print(f"  ⚠️ Ошибка колонки: {e}")

conn.commit()
conn.close()
print("✅ Исправление БД завершено! Теперь имена таблиц и колонок чистые.")
