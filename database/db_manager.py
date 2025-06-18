import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict
import base64


class DatabaseManager:
    def __init__(self, db_path: str = "attendance.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                fingerprint_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                school_id TEXT UNIQUE NOT NULL,
                profile_picture BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Attendance logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_user(self, fingerprint_id: int, name: str, school_id: str,
                 profile_picture_path: Optional[str] = None) -> bool:
        """Add a new user to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Convert image to blob if provided
            profile_blob = None
            if profile_picture_path and os.path.exists(profile_picture_path):
                with open(profile_picture_path, 'rb') as f:
                    profile_blob = f.read()

            cursor.execute('''
                INSERT INTO users (fingerprint_id, name, school_id, profile_picture)
                VALUES (?, ?, ?, ?)
            ''', (fingerprint_id, name, school_id, profile_blob))

            conn.commit()
            conn.close()
            return True

        except sqlite3.IntegrityError as e:
            print(f"Database integrity error: {e}")
            return False
        except Exception as e:
            print(f"Database error: {e}")
            return False

    def get_user_by_fingerprint(self, fingerprint_id: int) -> Optional[Dict]:
        """Get user by fingerprint ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, fingerprint_id, name, school_id, profile_picture
                FROM users WHERE fingerprint_id = ?
            ''', (fingerprint_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'id': row[0],
                    'fingerprint_id': row[1],
                    'name': row[2],
                    'school_id': row[3],
                    'profile_picture': row[4]
                }
            return None

        except Exception as e:
            print(f"Database error: {e}")
            return None

    def log_attendance(self, user_id: int) -> bool:
        """Log attendance for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO attendance_logs (user_id)
                VALUES (?)
            ''', (user_id,))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Database error: {e}")
            return False

    def get_attendance_logs(self, start_date=None, end_date=None, student_filter=None) -> List[Dict]:
        """Get attendance logs with optional filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Updated query to include all required fields
            query = '''
                SELECT a.id, u.name, u.school_id, u.fingerprint_id, u.profile_picture, a.timestamp
                FROM attendance_logs a
                JOIN users u ON a.user_id = u.id
            '''

            params = []
            conditions = []

            # Add date filtering
            if start_date:
                conditions.append("a.timestamp >= ?")
                params.append(start_date.isoformat())

            if end_date:
                conditions.append("a.timestamp <= ?")
                params.append(end_date.isoformat())

            # Add student name/ID filtering
            if student_filter:
                conditions.append("(LOWER(u.name) LIKE ? OR LOWER(u.school_id) LIKE ?)")
                filter_param = f"%{student_filter.lower()}%"
                params.extend([filter_param, filter_param])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY a.timestamp DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'school_id': row[2],
                    'fingerprint_id': row[3],
                    'profile_picture': row[4],
                    'timestamp': row[5]
                }
                for row in rows
            ]

        except Exception as e:
            print(f"Database error: {e}")
            return []

    def get_attendance_record(self, record_id: int) -> Optional[Dict]:
        """Get a specific attendance record by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT a.id, u.name, u.school_id, u.fingerprint_id, u.profile_picture, a.timestamp
                FROM attendance_logs a
                JOIN users u ON a.user_id = u.id
                WHERE a.id = ?
            ''', (record_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'school_id': row[2],
                    'fingerprint_id': row[3],
                    'profile_picture': row[4],
                    'timestamp': row[5]
                }
            return None

        except Exception as e:
            print(f"Database error: {e}")
            return None

    def delete_attendance_record(self, record_id: int) -> bool:
        """Delete an attendance record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM attendance_logs WHERE id = ?', (record_id,))

            success = cursor.rowcount > 0
            conn.commit()
            conn.close()

            return success

        except Exception as e:
            print(f"Database error: {e}")
            return False

    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT fingerprint_id, name, school_id
                FROM users
                ORDER BY name
            ''')

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    'fingerprint_id': row[0],
                    'name': row[1],
                    'school_id': row[2]
                }
                for row in rows
            ]

        except Exception as e:
            print(f"Database error: {e}")
            return []

    def fingerprint_id_exists(self, fingerprint_id: int) -> bool:
        """Check if fingerprint ID already exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT 1 FROM users WHERE fingerprint_id = ?', (fingerprint_id,))
            result = cursor.fetchone()
            conn.close()

            return result is not None

        except Exception as e:
            print(f"Database error: {e}")
            return False

    def school_id_exists(self, school_id: str) -> bool:
        """Check if school ID already exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT 1 FROM users WHERE school_id = ?', (school_id,))
            result = cursor.fetchone()
            conn.close()

            return result is not None

        except Exception as e:
            print(f"Database error: {e}")
            return False