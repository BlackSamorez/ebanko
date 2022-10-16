import sqlite3

class Handler:
    def __init__(self):
        self.conn = sqlite3.connect('/persistent/bot/request.db')
        self.cursor = self.conn.cursor()
        self.CreateRequestsTable()

    def __del__(self):
        self.conn.close()

    def CreateRequestsTable(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
        request_id INTEGER PRIMARY KEY,
        result TEXT CHECK( result IN ('S','F') ) NOT NULL,
        chat_id INTEGER NOT NULL,
        prefix TEXT NOT NULL,
        suffix TEXT,
        time t_i DEFAULT (strftime('%s', 'now'))
    );''')

    def insert(self, chat_id: int, prefix: str, suffix: str):
        if suffix is not None:
            self.cursor.execute("INSERT INTO requests(result, chat_id, prefix, suffix) VALUES ('S', ?, ?, ?)", (chat_id, prefix, suffix))
        else:
            self.cursor.execute("INSERT INTO requests(result, chat_id, prefix) VALUES ('F', ?, ?)", (chat_id, prefix))

    def flush(self):
        self.conn.commit()
