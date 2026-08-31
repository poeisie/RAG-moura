import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config
from app.rag.ingest import (
    build_vector_store,
    load_documents,
    save_vector_store,
    split_documents,
)


def main() -> None:
    print(f"Lendo documentos de '{config.DATA_DIR}'...")
    documentos = load_documents()
    print(f"  {len(documentos)} documento(s) carregado(s).")

    chunks = split_documents(documentos)
    print(
        f"Chunking concluído: {len(chunks)} chunk(s) "
        f"(chunk_size={config.CHUNK_SIZE}, chunk_overlap={config.CHUNK_OVERLAP})."
    )

    print(f"Gerando embeddings com '{config.EMBEDDING_MODEL}' e indexando no FAISS...")
    vector_store = build_vector_store(chunks)

    save_vector_store(vector_store)
    print(f"Índice salvo em '{config.INDEX_DIR}'.")


if __name__ == "__main__":
    main()
