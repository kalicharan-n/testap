import sqlite3

DB_PATH = "app.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create mapping table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            project TEXT NOT NULL,
            app_name TEXT NOT NULL,
            UNIQUE(domain, project, app_name)
        )
    ''')

    # Create metric configuration table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    headers TEXT,
    body TEXT
)
    ''')

    # Create completed runs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS completed_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            project TEXT NOT NULL,
            run_id TEXT NOT NULL,
            test_id TEXT NOT NULL,
            UNIQUE(domain, project, run_id, test_id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized!")
