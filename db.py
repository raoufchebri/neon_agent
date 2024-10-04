import psycopg2
from psycopg2 import OperationalError
from functools import wraps

class ChatDB:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.connect()
        self.create_table()

    def connect(self):
        self.conn = psycopg2.connect(self.db_url)

    def reconnect(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except OperationalError as e:
                print(f"OperationalError: {e}")
                print("Attempting to reconnect to the database...")
                self.connect()
                return func(self, *args, **kwargs)
        return wrapper

    @reconnect
    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    chat_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    is_function_call BOOLEAN DEFAULT TRUE
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_id ON chat_history (chat_id)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history (timestamp)
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_chat (
                    user_id TEXT,
                    chat_id TEXT,
                    PRIMARY KEY (user_id, chat_id)
                )
            """)
            self.conn.commit()

    @reconnect
    def create_chat(self, chat_id: str, user_id: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_history (chat_id, role, content)
                VALUES (%s, %s, %s)
            """, (chat_id, '', ''))
            cur.execute("""
                INSERT INTO user_chat (user_id, chat_id)
                VALUES (%s, %s)
            """, (user_id, chat_id))
            self.conn.commit()

    @reconnect
    def get_chat_history(self, chat_id: str) -> list:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT role, content FROM chat_history
                WHERE chat_id = %s AND is_function_call = FALSE
            """, (chat_id,))
            result = cur.fetchall()
            return [{"role": row[0], "content": row[1]} for row in result]

    @reconnect
    def get_all_chat_history(self, chat_id: str) -> list:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT role, content FROM chat_history
                WHERE chat_id = %s
            """, (chat_id,))
            result = cur.fetchall()
            return [{"role": row[0], "content": row[1]} for row in result]

    @reconnect
    def update_chat_history(self, chat_id: str, role: str, content: str, is_function_call: bool) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_history (chat_id, role, content, is_function_call)
                VALUES (%s, %s, %s, %s)
            """, (chat_id, role, content, is_function_call))
            self.conn.commit()

    @reconnect
    def get_user_chats(self, user_id: str) -> list:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT chat_id FROM user_chat
                WHERE user_id = %s
            """, (user_id,))
            result = cur.fetchall()
            return [row[0] for row in result]
