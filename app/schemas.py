from typing import List, Optional

from pydantic import BaseModel, Field


class PerguntaRequest(BaseModel):
    pergunta: str = Field(..., min_length=3, description="Pergunta em linguagem natural")
    k: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Quantidade de trechos a recuperar (padrão: DEFAULT_K)",
    )


class Trecho(BaseModel):
    fonte: str
    titulo: str
    conteudo: str


class RespostaResponse(BaseModel):
    resposta: str
    fontes: List[str]
    trechos_usados: List[Trecho]
