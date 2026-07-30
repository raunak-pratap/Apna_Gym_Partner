from pathlib import Path
import sqlite3
import streamlit as st

# -------------------------------------------------------------------
# Database configuration
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "data.db"


# -------------------------------------------------------------------
# Database connection
# -------------------------------------------------------------------

@st.cache_resource
def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(
        str(DB_PATH),
        check_same_thread=False,
    )

    conn.row_factory = sqlite3.Row

    # Better performance for concurrent reads/writes
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")

    return conn


# -------------------------------------------------------------------
# Database initialization
# -------------------------------------------------------------------

def init_db() -> None:
    conn = _get_connection()

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                reps INTEGER NOT NULL DEFAULT 0,
                sets INTEGER NOT NULL DEFAULT 0,
                time INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )


# -------------------------------------------------------------------
# User functions
# -------------------------------------------------------------------

def get_user(username: str):
    conn = _get_connection()

    return conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    ).fetchone()


def create_user(username: str):
    conn = _get_connection()

    try:
        with conn:
            conn.execute(
                "INSERT INTO users (username) VALUES (?)",
                (username,),
            )

    except sqlite3.IntegrityError:
        # Another request already created this username
        pass

    return get_user(username)


def get_or_create_user(username: str):
    user = get_user(username)

    if user is None:
        user = create_user(username)

    return user


# -------------------------------------------------------------------
# Exercise functions
# -------------------------------------------------------------------

def add_exercise(
    user_id: int,
    exercise_name: str,
    reps: int,
    sets: int,
    workout_time: int,
):
    conn = _get_connection()

    with conn:
        existing = conn.execute(
            """
            SELECT id
            FROM exercises
            WHERE user_id = ?
              AND exercise_name = ?
              AND DATE(created_at) = DATE('now')
            """,
            (
                user_id,
                exercise_name,
            ),
        ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE exercises
                SET
                    reps = reps + ?,
                    sets = sets + ?,
                    time = time + ?
                WHERE id = ?
                """,
                (
                    reps,
                    sets,
                    workout_time,
                    existing["id"],
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO exercises (
                    user_id,
                    exercise_name,
                    reps,
                    sets,
                    time
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    exercise_name,
                    reps,
                    sets,
                    workout_time,
                ),
            )


def get_users_exercises(user_id: int):
    conn = _get_connection()

    return conn.execute(
        """
        SELECT *
        FROM exercises
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,),
    ).fetchall()
