from functools import lru_cache
from typing import List, Optional

from langchain_core.documents import Document

from app import config
from app.rag.ingest import load_vector_store


@lru_cache(maxsize=1)
def _get_vector_store():
    return load_vector_store()


def retrieve_chunks(pergunta: str, k: Optional[int] = None) -> List[Document]:
    k = k or config.DEFAULT_K
    vector_store = _get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(pergunta)
