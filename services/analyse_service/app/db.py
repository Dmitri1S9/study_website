import os
from pathlib import Path
from typing import List, Optional

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
                self.log.error("😡😡😡😡😡 Exception in DB context", exc_info=(exc_type, exc_val, exc_tb))
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
            self.log.exception("😡😡😡😡😡 DB connection test failed")
            raise

class DBPost(DBConnection):
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
                  universe_id BIGINT NOT NULL REFERENCES universes(id) ON DELETE RESTRICT,
                  name TEXT NOT NULL,
                  UNIQUE (universe_id, name)
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
            self.log.info("👽👽👽👽👽 table profiles created")
            self.conn.commit()

    def create_table_entries(self) -> str:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS character_entries (
                  id BIGSERIAL PRIMARY KEY,
                  character_id BIGINT NOT NULL UNIQUE REFERENCES characters(id) ON DELETE RESTRICT,
                  profile_id BIGINT NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT
                );
            """)
            self.log.info("👽👽👽👽👽 table  created")
            self.conn.commit()

    def _addition_table(self, params: tuple, sql: str, method_create) -> str:
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

    def addition_table_universes(self, universe_name: str) -> str:
        sql = f"""
            INSERT INTO universes (name)
            VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id;
        """
        return self._addition_table((universe_name,), sql, self.create_table_universes)

    def addition_table_characters(self, character_name: str, universe_id) -> str:
        sql = f"""
            INSERT INTO characters (universe_id, name)
            VALUES (%s, %s)
            ON CONFLICT (universe_id, name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id;
        """
        return self._addition_table((universe_id, character_name), sql, self.create_table_characters)

    def addition_table_profiles(self, profile: dict) -> str:
        sql = f"""
            INSERT INTO profiles (profile)
            VALUES (%s)
            ON CONFLICT (profile) DO UPDATE SET profile = EXCLUDED.profile
            RETURNING id;
        """
        return self._addition_table((Json(profile),), sql, self.create_table_profiles)

    def addition_table_entries(self, character_id: int, profile_id: int) -> str:
        sql = """
            INSERT INTO character_entries (character_id, profile_id)
            VALUES (%s, %s)
            ON CONFLICT (character_id) DO UPDATE SET profile_id = EXCLUDED.profile_id
            RETURNING id;
        """
        return self._addition_table((character_id, profile_id), sql, self.create_table_entries)
    
    
class DBGet(DBConnection):
    def get_character_id(self, character_name: str, universe: str) -> dict | None:
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                        SELECT c.id
                        FROM characters c
                        JOIN universes u ON u.id = c.universe_id
                        WHERE c.name = %s AND u.name = %s
                    """,
                    (character_name, universe),
                )
                return cur.fetchone()
        except Exception as e:
            self.log.exception("😡😡😡😡😡 get_character_id failed: %s", e)
            return None

    def get_character_profile(self, character_id: int) -> dict | None:
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                        SELECT profile FROM profiles
                        JOIN character_entries c ON c.profile_id = profiles.id
                        WHERE c.character_id = %s;
                     """,
                    (character_id,),
                )
                row = cur.fetchone()
                return row["profile"] if row else None
        except Exception as e:
            self.log.exception("😡😡😡😡😡 get_character_profile failed: %s", e)
            return None

    def get_characters_profiles(self, character_ids: List[int]) -> dict | None:
        profiles = []
        for c_id in character_ids:
            profiles.append(self.get_character_profile(c_id))

        return profiles

    def get_universes_ids(self):
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                        SELECT id FROM universes;
                    """
                )
                row = cur.fetchall()
                return [r["id"] for r in row] if row else None
        except Exception as e:
            self.log.exception("😡😡😡😡😡 get_universes_ids failed", e)
            return None

    def get_all_characters_ids_from_universe(self, universes_id = int) -> dict | None:
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                        SELECT id FROM public.characters
                        WHERE universe_id = %s;
                     """,
                    (universes_id,),
                )
                row = cur.fetchall()
                return [r["id"] for r in row]  if row else None
        except Exception as e:
            self.log.exception("😡😡😡😡😡 get_all_characters_ids_from_universe failed", e)
            return None

    def get_all_characters(self):
        universes_ids = self.get_universes_ids()
        characters_ids = []
        for universe_id in universes_ids:
            characters_ids.extend(self.get_all_characters_ids_from_universe(universe_id))
        characters_profiles = self.get_characters_profiles(characters_ids)
        return characters_profiles

if __name__ == "__main__":
    ...