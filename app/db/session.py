import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app import config


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conexao = sqlite3.connect(config.DB_PATH)
    conexao.row_factory = sqlite3.Row
    try:
        yield conexao
    finally:
        conexao.close()
