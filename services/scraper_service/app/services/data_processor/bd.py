import os
from typing import Any

import psycopg2
from psycopg2.extras import execute_values
from contextlib import contextmanager

class BaseDB:
    def __init__(self):
        self.db_name = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")

    @contextmanager
    def get_conn(self):
        conn = psycopg2.connect(
            dbname=self.db_name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        try:
            yield conn
        finally:
            conn.close()

    def init_table(self):
        create_sql = """
        CREATE TABLE IF NOT EXISTS raw_texts (
            id SERIAL PRIMARY KEY,
            post_id TEXT,
            character_name TEXT,
            score INT,
            text TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(create_sql)
            conn.commit()

    def insert_many(self, records: list[tuple]):
        """
        records: (post_id, character_name, score, text)
        """
        if not records:
            return
        insert_sql = """
        INSERT INTO raw_texts (post_id, character_name, score, text)
        VALUES %s;
        """
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                execute_values(cur, insert_sql, records)
            conn.commit()

    def get_character(self, character_name: str) -> list[tuple]:
        select_sql = """
            SELECT *
            FROM public.raw_texts
            WHERE character_name = %s;
        """
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(select_sql, (character_name,))
                return cur.fetchall()

    def get_character_ids(self, character_name: str) -> list[tuple[Any, ...]]:
        select_sql = """
            SELECT post_id
            FROM public.raw_texts
            WHERE character_name = %s;
        """
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(select_sql, (character_name,))
                return cur.fetchall()