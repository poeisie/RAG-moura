from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app import config

EXTENSOES_SUPORTADAS = (".md", ".txt")


def load_documents(data_dir: Path = config.DATA_DIR) -> List[Document]:
    documentos: List[Document] = []

    for caminho in sorted(Path(data_dir).iterdir()):
        if caminho.suffix.lower() not in EXTENSOES_SUPORTADAS:
            continue

        texto = caminho.read_text(encoding="utf-8")
        primeira_linha = texto.strip().splitlines()[0] if texto.strip() else caminho.stem
        titulo = primeira_linha.lstrip("#").strip()

        documentos.append(
            Document(
                page_content=texto,
                metadata={"source": caminho.name, "title": titulo},
            )
        )

    return documentos


def split_documents(
    documentos: List[Document],
    chunk_size: int = config.CHUNK_SIZE,
    chunk_overlap: int = config.CHUNK_OVERLAP,
) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(documentos)


def get_embeddings():
    from langchain_community.embeddings import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)


def build_vector_store(chunks: List[Document]):
    from langchain_community.vectorstores import FAISS

    embeddings = get_embeddings()
    return FAISS.from_documents(chunks, embeddings)


def save_vector_store(vector_store, index_dir: Path = config.INDEX_DIR) -> None:
    index_dir = Path(index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(index_dir))


def load_vector_store(index_dir: Path = config.INDEX_DIR):
    from langchain_community.vectorstores import FAISS

    embeddings = get_embeddings()
    return FAISS.load_local(
        str(index_dir),
        embeddings,
        allow_dangerous_deserialization=True,
    )
