import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

def get_sqlite_saver() -> SqliteSaver:
    conn = sqlite3.connect("memory.db", check_same_thread = False)
    memory = SqliteSaver(conn)
    
    return memory


