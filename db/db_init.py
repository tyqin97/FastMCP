"""
Initialize the database for testing.
Instructions: YOU ONLY NEED TO RUN THIS FILE ONCE TO INITIALIZE THE DATABASE.
"""

import sqlite3

conn = sqlite3.connect("db/test.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL
)
""")

cursor.execute("""
INSERT INTO users (name, email) VALUES
('John Doe', 'john@example.com'),
('Jane Doe', 'jane@example.com'),
('Jim Doe', 'jim@example.com'),
('Billy Doe', 'billy@example.com'),
('Jack Doe', 'jack@example.com'),
('Jill Doe', 'jill@example.com')
""")

conn.commit()
conn.close()

print("Database initialized successfully.")