# FILE: database.py
# SQLite database module for storing research queries and results

import os
import sqlite3
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Database file path
DB_PATH = os.getenv("DB_PATH", "research_data.db")


def get_connection():
    """Get a SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables."""
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Create research_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create search_results table for storing individual search results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                results TEXT,  -- JSON array of search results
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES research_sessions(id) ON DELETE CASCADE
            )
        """)

        # Create scraped_pages table for storing scraped content
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES research_sessions(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        print(f"Database initialized at {DB_PATH}")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()


def create_session(query: str) -> int:
    """Create a new research session."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO research_sessions (query, status) VALUES (?, ?)",
            (query, "pending"),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_session(session_id: int, response: str, status: str = "completed"):
    """Update a research session with the response."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE research_sessions
            SET response = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (response, status, session_id),
        )
        conn.commit()
    finally:
        conn.close()


def save_search_results(session_id: int, query: str, results: list):
    """Save search results for a session."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO search_results (session_id, query, results) VALUES (?, ?, ?)",
            (session_id, query, json.dumps(results)),
        )
        conn.commit()
    finally:
        conn.close()


def save_scraped_page(session_id: int, url: str, content: str):
    """Save scraped page content for a session."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO scraped_pages (session_id, url, content) VALUES (?, ?, ?)",
            (session_id, url, content),
        )
        conn.commit()
    finally:
        conn.close()


def get_session(session_id: int) -> Optional[dict]:
    """Get a research session by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM research_sessions WHERE id = ?",
            (session_id,),
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def get_session_search_results(session_id: int) -> list:
    """Get all search results for a session."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM search_results WHERE session_id = ? ORDER BY created_at",
            (session_id,),
        )
        rows = cursor.fetchall()
        results = []
        for row in rows:
            row_dict = dict(row)
            row_dict["results"] = json.loads(row_dict["results"]) if row_dict["results"] else []
            results.append(row_dict)
        return results
    finally:
        conn.close()


def get_session_scraped_pages(session_id: int) -> list:
    """Get all scraped pages for a session."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM scraped_pages WHERE session_id = ? ORDER BY created_at",
            (session_id,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_all_sessions(limit: int = 50) -> list:
    """Get all research sessions, most recent first."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, query, status, created_at, updated_at
            FROM research_sessions
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_session(session_id: int) -> bool:
    """Delete a research session and all associated data."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM research_sessions WHERE id = ?", (session_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# Initialize database on module import
init_db()
