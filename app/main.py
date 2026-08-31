from fastapi import FastAPI, HTTPException

from app import config
from app.rag.retriever import retrieve_chunks
from app.schemas import PerguntaRequest, RespostaResponse, Trecho

app = FastAPI(
    title="Assistente Inteligente de Consulta a Documentos Corporativos — Grupo Moura",
    version="0.1.0",
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
        chunks = retrieve_chunks(request.pergunta, request.k)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Índice vetorial não encontrado. Rode 'python scripts/build_index.py' "
                "antes de consultar a API."
            ),
        ) from exc

    if not chunks:
        return RespostaResponse(
            resposta="Não encontrado nos documentos disponíveis.",
            fontes=[],
            trechos_usados=[],
        )

    trechos_usados = [
        Trecho(
            fonte=chunk.metadata.get("source", "desconhecido"),
            titulo=chunk.metadata.get("title", ""),
            conteudo=chunk.page_content,
        )
        for chunk in chunks
    ]
    fontes = sorted({trecho.fonte for trecho in trechos_usados})

    return RespostaResponse(
        resposta="[Fase 3: resposta ainda não gerada por LLM — ver trechos recuperados abaixo]",
        fontes=fontes,
        trechos_usados=trechos_usados,
    )
