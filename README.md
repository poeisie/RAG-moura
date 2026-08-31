# Assistente Inteligente de Consulta a Documentos Corporativos — Grupo Moura

MVP de um assistente RAG (Retrieval-Augmented Generation) que responde perguntas em linguagem
natural com base em documentos corporativos fictícios, sempre citando a fonte usada. Construído
para o desafio técnico de estágio em Engenharia de Software e IA do Grupo Moura.

## Como funciona (arquitetura)

```
Pergunta (usuário)
      │
      ▼
POST /perguntar  (FastAPI)
      │
      ▼
retrieve_chunks()  ──►  índice FAISS (embeddings locais, sentence-transformers)
      │
      ▼
chain.responder_pergunta()
      │   monta o prompt com os trechos recuperados, rotulados por fonte
      ▼
chamar_llm()  ──►  OpenRouter (modelo gratuito)
      │
      ▼
resposta + fontes citadas  ──►  salva no SQLite (histórico)  ──►  devolvida ao usuário
```

Indexação (rodada uma vez, offline, via `scripts/build_index.py`):

```
data/*.md  ──►  load_documents()  ──►  split_documents() (chunking)
           ──►  embeddings (sentence-transformers)  ──►  índice FAISS (index_store/)
```

## Estrutura do projeto

```
.
├── app/
│   ├── main.py            # aplicação FastAPI (endpoints)
│   ├── config.py          # variáveis de ambiente centralizadas
│   ├── schemas.py         # modelos Pydantic de request/response
│   ├── rag/
│   │   ├── ingest.py       # carregamento, chunking, índice FAISS
│   │   ├── retriever.py    # busca (retrieval) no índice
│   │   ├── llm_client.py   # cliente HTTP do OpenRouter
│   │   └── chain.py        # orquestra retrieval + prompt + geração
│   └── db/
│       ├── session.py      # conexão SQLite
│       └── models.py       # criação de tabela + CRUD do histórico
├── data/                   # 5 documentos corporativos fictícios (.md)
├── scripts/
│   └── build_index.py      # (re)gera o índice FAISS a partir de data/
├── tests/                  # suíte pytest (13 testes)
├── requirements.txt
├── .env.example
└── pyproject.toml          # configuração do pytest
```

## Como rodar

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edite .env e preencha OPENROUTER_API_KEY (gratuita em https://openrouter.ai/)

python scripts/build_index.py      # gera o índice vetorial a partir de data/
uvicorn app.main:app --reload      # sobe a API em http://127.0.0.1:8000
```

Documentação interativa (Swagger): `http://127.0.0.1:8000/docs`.

## Endpoints

| Método | Rota          | Descrição                                                             |
| ------ | ------------- | --------------------------------------------------------------------- |
| GET    | `/health`     | Checagem simples de disponibilidade.                                  |
| GET    | `/documentos` | Lista os documentos disponíveis em `data/`.                           |
| POST   | `/perguntar`  | `{"pergunta": str, "k": int opcional}` → resposta + fontes citadas.   |
| GET    | `/historico`  | `?limite=N` (padrão 10) — últimas interações, mais recentes primeiro. |

Exemplo:

```bash
curl -X POST http://127.0.0.1:8000/perguntar \
  -H "Content-Type: application/json" \
  -d '{"pergunta": "Quantos dias de férias eu tenho direito?", "k": 3}'
```

```json
{
  "resposta": "Você tem direito a 30 dias corridos de férias após 12 meses de trabalho. [politica_de_ferias.md]",
  "fontes": ["politica_de_ferias.md"],
  "trechos_usados": [
    {
      "fonte": "politica_de_ferias.md",
      "titulo": "Política de Férias — Grupo Moura",
      "conteudo": "..."
    }
  ]
}
```

Se a pergunta não tiver relação com os documentos, a resposta é `"Não encontrado nos documentos disponíveis."`, sem fontes.

## Como rodar os testes

```bash
pytest -v
```
