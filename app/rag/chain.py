from typing import Dict, List, Optional

from langchain_core.documents import Document

from app.rag.llm_client import chamar_llm
from app.rag.retriever import retrieve_chunks

PROMPT_SISTEMA = """Você é o assistente virtual de RH/TI do Grupo Moura.

Regras:
1. Responda SOMENTE com base no CONTEXTO fornecido abaixo, extraído dos documentos internos.
2. Nunca use conhecimento geral ou externo ao CONTEXTO, mesmo que você "saiba" a resposta.
3. Se a resposta não estiver no CONTEXTO, responda exatamente:
   "Não encontrado nos documentos disponíveis."
4. Ao final, cite a(s) fonte(s) usada(s) entre colchetes, pelo nome do arquivo
   (ex.: [politica_de_ferias.md]).
5. Seja objetivo e claro, em português."""


def _montar_contexto(chunks: List[Document]) -> str:
    partes = []
    for chunk in chunks:
        fonte = chunk.metadata.get("source", "desconhecido")
        partes.append(f"[Fonte: {fonte}]\n{chunk.page_content}")
    return "\n\n---\n\n".join(partes)


def responder_pergunta(pergunta: str, k: Optional[int] = None) -> Dict:
    chunks = retrieve_chunks(pergunta, k)

    if not chunks:
        return {
            "resposta": "Não encontrado nos documentos disponíveis.",
            "fontes": [],
            "trechos_usados": [],
        }

    contexto = _montar_contexto(chunks)
    mensagens = [
        {"role": "system", "content": PROMPT_SISTEMA},
        {"role": "user", "content": f"CONTEXTO:\n{contexto}\n\nPERGUNTA:\n{pergunta}"},
    ]

    resposta_texto = chamar_llm(mensagens)
    fontes = sorted({chunk.metadata.get("source", "desconhecido") for chunk in chunks})

    return {"resposta": resposta_texto, "fontes": fontes, "trechos_usados": chunks}
