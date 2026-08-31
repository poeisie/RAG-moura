from pathlib import Path

from langchain_core.documents import Document

from app.rag.ingest import load_documents, split_documents


def test_load_documents_le_apenas_arquivos_md_e_txt(tmp_path: Path) -> None:
    (tmp_path / "doc1.md").write_text("# Título 1\nConteúdo do primeiro documento.", encoding="utf-8")
    (tmp_path / "doc2.md").write_text("# Título 2\nConteúdo do segundo documento.", encoding="utf-8")
    (tmp_path / "ignorar.pdf").write_text("não deve ser lido", encoding="utf-8")

    documentos = load_documents(tmp_path)

    assert len(documentos) == 2
    fontes = {documento.metadata["source"] for documento in documentos}
    assert fontes == {"doc1.md", "doc2.md"}


def test_load_documents_extrai_titulo_do_cabecalho(tmp_path: Path) -> None:
    (tmp_path / "unico.md").write_text("# Meu Título\nTexto qualquer.", encoding="utf-8")

    [documento] = load_documents(tmp_path)

    assert documento.metadata["title"] == "Meu Título"
    assert documento.metadata["source"] == "unico.md"


def test_split_documents_gera_mais_de_um_chunk_para_texto_longo() -> None:
    texto_longo = "Parágrafo de teste. " * 200
    documentos = [Document(page_content=texto_longo, metadata={"source": "grande.md"})]

    chunks = split_documents(documentos, chunk_size=500, chunk_overlap=50)

    assert len(chunks) > 1
    assert all(chunk.metadata["source"] == "grande.md" for chunk in chunks)


def test_load_documents_com_a_base_real_do_projeto() -> None:
    documentos = load_documents(Path("data"))

    assert len(documentos) == 5
    assert all(documento.page_content.strip() for documento in documentos)
