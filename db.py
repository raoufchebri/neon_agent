from tinydb import TinyDB, Query

class ChatDB:
    def __init__(self, db_path: str = 'chat_history.json'):
        self.db = TinyDB(db_path)
        self.chat_table = self.db.table('chat_history')

    def create_chat(self, chat_id: str) -> None:
        self.chat_table.insert({'chat_id': chat_id, 'messages': []})

    def get_chat_history(self, chat_id: str) -> list:
        chat_history = self.chat_table.get(Query().chat_id == chat_id)
        return chat_history['messages'] if chat_history else []

    def update_chat_history(self, chat_id: str, role: str, content: str) -> None:
        messages = self.get_chat_history(chat_id)
        messages.append({"role": role, "content": content})
        self.chat_table.update({'messages': messages}, Query().chat_id == chat_id)
