"""
TruthLens AI – SQLite Schema Migration
Adds new columns to the users table for the expanded profile system.
"""
import sqlite3
import os

# Match app/core/config.py: Vercel's task dir is read-only, so route the DB
# to /tmp when running on Vercel; otherwise use the local relative path.
db_path = '/tmp/truthlens.db' if os.environ.get('VERCEL_ENV') else 'truthlens.db'

if not os.path.exists(db_path):
    print(f"Database '{db_path}' not found. It will be created fresh on next startup.")
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    existing = [row[1] for row in cur.execute('PRAGMA table_info(users)').fetchall()]
    print(f"Existing user columns: {existing}")

    migrations = []

    if 'full_name' not in existing:
        cur.execute('ALTER TABLE users ADD COLUMN full_name TEXT')
        migrations.append('full_name')

    if 'role' not in existing:
        cur.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
        migrations.append('role')

    if 'is_active' not in existing:
        cur.execute('ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1')
        migrations.append('is_active')

    if 'last_login' not in existing:
        cur.execute('ALTER TABLE users ADD COLUMN last_login DATETIME')
        migrations.append('last_login')

    conn.commit()
    conn.close()

    if migrations:
        print(f"Migration complete. Added columns: {', '.join(migrations)}")
    else:
        print("No migration needed. Schema is up to date.")
