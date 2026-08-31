import json
from datetime import datetime, timezone
from typing import Dict, List

from app.db.session import get_connection

CRIAR_TABELA_SQL = """
CREATE TABLE IF NOT EXISTS interacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    fontes TEXT NOT NULL,
    k_usado INTEGER,
    criado_em TEXT NOT NULL
);
"""


def init_db() -> None:
    with get_connection() as conexao:
        conexao.execute(CRIAR_TABELA_SQL)
        conexao.commit()


def salvar_interacao(pergunta: str, resposta: str, fontes: List[str], k_usado: int) -> int:
    with get_connection() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO interacoes (pergunta, resposta, fontes, k_usado, criado_em)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                pergunta,
                resposta,
                json.dumps(fontes, ensure_ascii=False),
                k_usado,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conexao.commit()
        return cursor.lastrowid


def listar_interacoes(limite: int = 10) -> List[Dict]:
    with get_connection() as conexao:
        linhas = conexao.execute(
            """
            SELECT id, pergunta, resposta, fontes, k_usado, criado_em
            FROM interacoes
            ORDER BY id DESC
            LIMIT ?
            """,
            (limite,),
        ).fetchall()

    return [
        {
            "id": linha["id"],
            "pergunta": linha["pergunta"],
            "resposta": linha["resposta"],
            "fontes": json.loads(linha["fontes"]),
            "k_usado": linha["k_usado"],
            "criado_em": linha["criado_em"],
        }
        for linha in linhas
    ]
