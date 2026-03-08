from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Database setup function
def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    # Table for students and seats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            seat_no TEXT UNIQUE,
            fees_due REAL,
            status TEXT DEFAULT 'Unpaid'
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    conn.close()
    return f"Welcome to Aspirant Library ERP! Total Students: {len(data)}"

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=8080)
