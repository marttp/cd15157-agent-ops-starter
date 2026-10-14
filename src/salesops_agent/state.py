"""Local authenticated sessions and sanitized, replayable run history."""

import hashlib
import json
import os
import secrets
import sqlite3
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage


class StateStore:
    def __init__(self, path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, salt BLOB, password_hash BLOB);
                CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, owner TEXT NOT NULL REFERENCES users(user_id));
                CREATE TABLE IF NOT EXISTS history (run_id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(session_id), question TEXT NOT NULL, answer TEXT NOT NULL, trace TEXT NOT NULL);
            """)
        os.chmod(path, 0o600)

    def connection(self):
        db = sqlite3.connect(self.path)
        db.execute("PRAGMA foreign_keys=ON")
        return db

    @staticmethod
    def password_hash(password, salt):
        return hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)

    def create_user(self, user, password):
        if not user or len(user) > 100 or len(password) < 12:
            raise ValueError("user_required_and_password_minimum_12_characters")
        salt = secrets.token_bytes(16)
        with self.connection() as db:
            db.execute(
                "INSERT INTO users VALUES (?, ?, ?)",
                (user, salt, self.password_hash(password, salt)),
            )

    def authenticate(self, user, password):
        with self.connection() as db:
            row = db.execute(
                "SELECT salt, password_hash FROM users WHERE user_id=?", (user,)
            ).fetchone()
        if not row or not secrets.compare_digest(row[1], self.password_hash(password, row[0])):
            raise ValueError("authentication_failed")
        # Opaque local identity proof. It is never a tool argument or model context value.
        return Principal(user, self)

    def create_session(self, principal):
        self.validate_principal(principal)
        sid = str(uuid4())
        with self.connection() as db:
            db.execute("INSERT INTO sessions VALUES (?, ?)", (sid, principal.user_id))
        return sid

    def validate_principal(self, principal):
        if not isinstance(principal, Principal) or principal.store is not self:
            raise ValueError("authenticated_principal_required")

    def assert_owner(self, principal, session_id):
        self.validate_principal(principal)
        with self.connection() as db:
            row = db.execute(
                "SELECT owner FROM sessions WHERE session_id=?", (session_id,)
            ).fetchone()
        if row is None or row[0] != principal.user_id:
            raise ValueError("session_access_denied")

    def sessions(self, principal):
        self.validate_principal(principal)
        with self.connection() as db:
            return [
                row[0]
                for row in db.execute(
                    "SELECT session_id FROM sessions WHERE owner=?", (principal.user_id,)
                )
            ]

    def messages(self, principal, session_id):
        self.assert_owner(principal, session_id)
        with self.connection() as db:
            rows = db.execute(
                "SELECT question, answer FROM history WHERE session_id=? ORDER BY rowid DESC LIMIT 5",
                (session_id,),
            ).fetchall()
        return [message for q, a in reversed(rows) for message in (HumanMessage(q), AIMessage(a))]

    def record(self, principal, session_id, result, trace):
        self.assert_owner(principal, session_id)
        with self.connection() as db:
            db.execute(
                "INSERT OR IGNORE INTO history VALUES (?, ?, ?, ?, ?)",
                (result["run_id"], session_id, trace["input"], result["answer"], json.dumps(trace)),
            )

    def replay(self, principal, run_id):
        self.validate_principal(principal)
        with self.connection() as db:
            row = db.execute(
                "SELECT h.trace FROM history h JOIN sessions s ON h.session_id=s.session_id WHERE h.run_id=? AND s.owner=?",
                (run_id, principal.user_id),
            ).fetchone()
        if not row:
            raise ValueError("run_access_denied")
        return json.loads(row[0])


class Principal:
    def __init__(self, user_id, store):
        self.user_id, self.store = user_id, store
