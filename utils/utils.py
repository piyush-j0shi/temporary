"""Utility functions for the application.

This module provides utility functions, such as a function to get a SQLite saver.
"""

import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

def get_sqlite_saver() -> SqliteSaver:
    """Returns a SqliteSaver instance for managing checkpoints.

    This function creates a SQLite connection and initializes a SqliteSaver
    object with it. The connection is configured to allow access from multiple
    threads.

    Returns:
        A SqliteSaver instance.
    """
    conn = sqlite3.connect("memory.db", check_same_thread = False)
    memory = SqliteSaver(conn)
    
    return memory


