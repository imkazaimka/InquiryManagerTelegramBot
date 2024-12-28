"""
Programmer : Shoniyozov Imronbek 

Filename : models.py

Description : Database models and functions for managing inquiries
"""

import logging
import os
import sqlite3

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Define database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DB_NAME = os.path.join(DATABASE_DIR, "inquiries.db")

# Ensure the database folder exists
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            name TEXT,
            surname TEXT,
            phone TEXT,
            workplace TEXT,
            role TEXT,
            inquiry TEXT,
            answer TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_inquiry(user_id, username, name, surname, phone, workplace, role, inquiry_text):
    logger.info(f"Inserting inquiry with data: user_id={user_id}, username={username}, "
                f"name={name}, surname={surname}, phone={phone}, workplace={workplace}, role={role}, inquiry={inquiry_text}")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO inquiries (user_id, username, name, surname, phone, workplace, role, inquiry, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'unanswered')
        ''', (user_id, username, name, surname, phone, workplace, role, inquiry_text))

        conn.commit()
        inquiry_id = cursor.lastrowid
        logger.info(f"Inquiry inserted with ID: {inquiry_id}")
        return inquiry_id
    except Exception as e:
        logger.error(f"Error inserting inquiry: {e}")
        raise
    finally:
        conn.close()

def get_inquiry(inquiry_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries WHERE id = ?', (inquiry_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_inquiry_answer(inquiry_id, answer_text):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE inquiries
        SET answer = ?, status = 'answered'
        WHERE id = ?
    ''', (answer_text, inquiry_id))
    conn.commit()
    conn.close()

def filter_inquiries_by_status(status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, user_id, workplace, status
        FROM inquiries
        WHERE status = ?
        ORDER BY timestamp DESC
    ''', (status,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def filter_inquiries_by_workplace(workplace):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, user_id, workplace, status
        FROM inquiries
        WHERE workplace = ?
        ORDER BY timestamp DESC
    ''', (workplace,))
    rows = cursor.fetchall()
    conn.close()
    return rows
