import sqlite3, os
DB = "shoe_store.db"
if not os.path.exists(DB): 
    print("❌ shoe_store.db не найден! Проверь путь."); exit()

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 1. Чистим пробелы в таблицах
for old in [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '% ';")]:
    new = old.strip()
    print(f"📦 Таблица: '{old}' → '{new}'")
    cur.execute(f'ALTER TABLE "{old}" RENAME TO "{new}";')

# 2. Чистим пробелы в колонках
for tbl in [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table';")]:
    for col in cur.execute(f'PRAGMA table_info("{tbl}");').fetchall():
        old_c, new_c = col[1], col[1].strip()
        if old_c != new_c:
            try:
                cur.execute(f'ALTER TABLE "{tbl}" RENAME COLUMN "{old_c}" TO "{new_c}";')
                print(f"  📝 {tbl}.{old_c} → {new_c}")
            except: pass
conn.commit(); conn.close()
print("✅ Схема БД полностью очищена от пробелов.")
