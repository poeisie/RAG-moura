from pathlib import Path

import pytest

from app import config
from app.db import models


@pytest.fixture
def banco_temporario(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    caminho = tmp_path / "teste.db"
    monkeypatch.setattr(config, "DB_PATH", caminho)
    models.init_db()
    return caminho


def test_salvar_e_listar_interacoes(banco_temporario: Path) -> None:
    models.salvar_interacao("Pergunta 1", "Resposta 1", ["doc1.md"], 3)
    models.salvar_interacao("Pergunta 2", "Resposta 2", ["doc2.md", "doc3.md"], 4)

    historico = models.listar_interacoes(limite=10)

    assert len(historico) == 2
    assert historico[0]["pergunta"] == "Pergunta 2"
    assert historico[0]["fontes"] == ["doc2.md", "doc3.md"]
    assert historico[1]["k_usado"] == 3


def test_listar_interacoes_respeita_limite(banco_temporario: Path) -> None:
    for indice in range(5):
        models.salvar_interacao(f"Pergunta {indice}", f"Resposta {indice}", [], 4)

    historico = models.listar_interacoes(limite=2)

    assert len(historico) == 2


def test_listar_interacoes_em_banco_vazio(banco_temporario: Path) -> None:
    assert models.listar_interacoes() == []
