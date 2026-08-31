from contextlib import asynccontextmanager
from typing import AsyncIterator, List

from fastapi import FastAPI, HTTPException, Query

from app import config
from app.db.models import init_db, listar_interacoes, salvar_interacao
from app.rag.chain import responder_pergunta
from app.rag.llm_client import LLMError
from app.schemas import InteracaoHistorico, PerguntaRequest, RespostaResponse, Trecho


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(
    title="Assistente Inteligente de Consulta a Documentos Corporativos — Grupo Moura",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/documentos")
def listar_documentos() -> dict:
    arquivos = sorted(
        p.name for p in config.DATA_DIR.iterdir() if p.suffix.lower() in (".md", ".txt")
    )
    return {"documentos": arquivos}


@app.post("/perguntar", response_model=RespostaResponse)
def perguntar(request: PerguntaRequest) -> RespostaResponse:
    try:
        resultado = responder_pergunta(request.pergunta, request.k)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Índice vetorial não encontrado. Rode 'python scripts/build_index.py' "
                "antes de consultar a API."
            ),
        ) from exc
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    salvar_interacao(
        pergunta=request.pergunta,
        resposta=resultado["resposta"],
        fontes=resultado["fontes"],
        k_usado=request.k or config.DEFAULT_K,
    )

    trechos_usados = [
        Trecho(
            fonte=chunk.metadata.get("source", "desconhecido"),
            titulo=chunk.metadata.get("title", ""),
            conteudo=chunk.page_content,
        )
        for chunk in resultado["trechos_usados"]
    ]

    return RespostaResponse(
        resposta=resultado["resposta"],
        fontes=resultado["fontes"],
        trechos_usados=trechos_usados,
    )


@app.get("/historico", response_model=List[InteracaoHistorico])
def historico(limite: int = Query(default=10, ge=1, le=100)) -> List[InteracaoHistorico]:
    return listar_interacoes(limite)
