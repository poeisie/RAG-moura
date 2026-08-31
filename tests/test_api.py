from pathlib import Path
from typing import Iterator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from langchain_core.documents import Document

from app import config


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "teste.db")

    import app.main as main_module

    with TestClient(main_module.app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    resposta = client.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_documentos_lista_os_5_arquivos_de_data(client: TestClient) -> None:
    resposta = client.get("/documentos")

    assert resposta.status_code == 200
    assert len(resposta.json()["documentos"]) == 5


def test_perguntar_retorna_resposta_e_grava_no_historico(client: TestClient) -> None:
    import app.main as main_module

    resultado_falso = {
        "resposta": "Você tem direito a 30 dias corridos de férias. [politica_de_ferias.md]",
        "fontes": ["politica_de_ferias.md"],
        "trechos_usados": [
            Document(
                page_content="trecho...",
                metadata={"source": "politica_de_ferias.md", "title": "Política de Férias"},
            )
        ],
    }

    with patch.object(main_module, "responder_pergunta", return_value=resultado_falso):
        resposta = client.post(
            "/perguntar", json={"pergunta": "Quantos dias de férias eu tenho?"}
        )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["fontes"] == ["politica_de_ferias.md"]
    assert len(corpo["trechos_usados"]) == 1

    historico = client.get("/historico").json()
    assert len(historico) == 1
    assert historico[0]["pergunta"] == "Quantos dias de férias eu tenho?"


def test_perguntar_pergunta_muito_curta_e_rejeitada(client: TestClient) -> None:
    resposta = client.post("/perguntar", json={"pergunta": "oi"})

    assert resposta.status_code == 422


def test_perguntar_indice_ausente_retorna_503(client: TestClient) -> None:
    import app.main as main_module

    with patch.object(main_module, "responder_pergunta", side_effect=FileNotFoundError()):
        resposta = client.post("/perguntar", json={"pergunta": "pergunta válida"})

    assert resposta.status_code == 503


def test_perguntar_erro_do_llm_retorna_502(client: TestClient) -> None:
    import app.main as main_module

    with patch.object(
        main_module, "responder_pergunta", side_effect=main_module.LLMError("falha simulada")
    ):
        resposta = client.post("/perguntar", json={"pergunta": "pergunta válida"})

    assert resposta.status_code == 502
