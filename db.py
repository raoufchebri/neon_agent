import psycopg2

class ChatDB:
    def __init__(self, db_url: str):
        self.conn = psycopg2.connect(db_url)
        self.create_table()

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    chat_id TEXT PRIMARY KEY,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_id ON chat_history (chat_id)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history (timestamp)
            """)
            self.conn.commit()

    def create_chat(self, chat_id: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_history (chat_id, role, content)
                VALUES (%s, %s, %s)
                ON CONFLICT (chat_id) DO NOTHING
            """, (chat_id, '', ''))
            self.conn.commit()

    def get_chat_history(self, chat_id: str) -> list:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT role, content FROM chat_history
                WHERE chat_id = %s
            """, (chat_id,))
            result = cur.fetchall()
            return [{"role": row[0], "content": row[1]} for row in result]

    def update_chat_history(self, chat_id: str, role: str, content: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_history (chat_id, role, content)
                VALUES (%s, %s, %s)
            """, (chat_id, role, content))
            self.conn.commit()
