from typing import Dict, List

import requests

from app import config


class LLMError(RuntimeError):
    """Erro ao chamar o provedor de LLM (configuração ausente, rede, resposta inesperada)."""


def chamar_llm(mensagens: List[Dict[str, str]], timeout: int = 30) -> str:
    if not config.OPENROUTER_API_KEY:
        raise LLMError(
            "OPENROUTER_API_KEY não configurada. Defina a variável no arquivo .env "
            "(veja .env.example)."
        )

    try:
        resposta = requests.post(
            config.OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": config.OPENROUTER_MODEL,
                "messages": mensagens,
                "temperature": 0,
            },
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise LLMError(f"Falha de conexão com o OpenRouter: {exc}") from exc

    if resposta.status_code != 200:
        raise LLMError(
            f"Falha ao chamar o LLM (status {resposta.status_code}): {resposta.text[:300]}"
        )

    corpo = resposta.json()
    try:
        return corpo["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise LLMError(f"Resposta em formato inesperado do LLM: {corpo}") from exc
