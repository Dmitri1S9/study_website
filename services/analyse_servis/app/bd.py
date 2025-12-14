import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from psycopg2.extras import Json
import logging


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class DBConnection:
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        self.log.debug("DB connection opened")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self.log.error("Exception in DB context", exc_info=(exc_type, exc_val, exc_tb))
                self.conn.rollback()
                self.log.debug("DB transaction rolled back")
            else:
                self.conn.commit()
                self.log.debug("DB transaction committed")
        finally:
            self.conn.close()
            self.log.debug("DB connection closed")
        return False

    def test_connection(self):
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT 1 AS ok;")
                self.log.debug("OK, connection works.")
        except psycopg2.Error:
            self.log.exception("DB connection test failed")
            raise

class DBWorker(DBConnection):
    def __init__(self):
        super().__init__()

    def create_table_universes(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS universes (
                        id BIGSERIAL PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE
                    ); 
            """)
            self.log.info("table universes created")
            self.conn.commit()

    def create_table_characters(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(""" 
                    CREATE TABLE IF NOT EXISTS characters (
                        id BIGSERIAL PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE
                    ); 
            """)
            self.log.info("table characters created")
            self.conn.commit()

    def create_table_profiles(self):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id BIGSERIAL PRIMARY KEY,
                    profile JSONB NOT NULL UNIQUE
                ); 
            """)
            self.log.info("table profiles created")
            self.conn.commit()

    def create_table_entries(self) -> str:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS character_entries (
                  id BIGSERIAL PRIMARY KEY,
                  universe_id BIGINT NOT NULL REFERENCES universes(id) ON DELETE RESTRICT,
                  character_id BIGINT NOT NULL REFERENCES characters(id) ON DELETE RESTRICT,
                  profile_id BIGINT NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
                  UNIQUE (universe_id, character_id)
                );
            """)
            self.log.info("table  created")
            self.conn.commit()

    def _update_table(self, params: tuple, sql: str, method_create) -> str:
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                return_id = cur.fetchone()[0]
                self.conn.commit()
                return return_id
        except psycopg2.errors.UndefinedTable:
            self.conn.rollback()
            method_create()
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                return_id = cur.fetchone()[0]
                self.conn.commit()
                return return_id

    def update_table_universes(self, universe_name: str) -> str:
        sql = f"""
            INSERT INTO universes (name)
            VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id;
        """
        return self._update_table((universe_name, ), sql, self.create_table_universes)

    def update_table_characters(self, character_name: str) -> str:
        sql = f"""
            INSERT INTO characters (name)
            VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id;
        """
        return self._update_table((character_name, ), sql, self.create_table_characters)

    def update_table_profiles(self, profile: dict) -> str:
        sql = f"""
            INSERT INTO profiles (profile)
            VALUES (%s)
            ON CONFLICT (profile) DO UPDATE SET profile = EXCLUDED.profile
            RETURNING id;
        """
        return self._update_table((Json(profile), ), sql, self.create_table_profiles)

    def update_table_entries(self, character_id: int, universe_id: int, profile_id: int) -> str:
        sql = """
           INSERT INTO character_entries (character_id, universe_id, profile_id)
           VALUES (%s, %s, %s)
           ON CONFLICT (character_id, universe_id) DO UPDATE SET profile_id = EXCLUDED.profile_id
           RETURNING id;
           """
        return self._update_table((character_id, universe_id, profile_id), sql, self.create_table_entries)

if __name__ == "__main__":
    ...