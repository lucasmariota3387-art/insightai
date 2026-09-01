"""
Módulo de tratamento de dados do InsightAI.

Responsável por: validar colunas obrigatórias, limpar valores inválidos,
converter tipos e criar colunas derivadas (como faturamento).
"""

import pandas as pd

COLUNAS_OBRIGATORIAS = ["data", "produto", "categoria", "quantidade", "preco"]


def validar_colunas(df: pd.DataFrame) -> list:
    """
    Verifica se todas as colunas obrigatórias estão presentes.

    A comparação é feita de forma normalizada (sem espaços extras e
    em minúsculas), para que cabeçalhos como "Produto", " PRODUTO"
    ou "produto " sejam aceitos antes mesmo da normalização definitiva
    feita em tratar_dados().

    Retorna a lista de colunas que estão faltando (vazia se tudo ok).
    """
    colunas_normalizadas = [str(col).strip().lower() for col in df.columns]

    faltando = [col for col in COLUNAS_OBRIGATORIAS if col not in colunas_normalizadas]

    return faltando


def tratar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica limpeza e transformação básica no DataFrame de vendas:
    - remove duplicados
    - converte tipos (data, quantidade, preco)
    - remove linhas com dados essenciais ausentes ou inválidos
    - cria a coluna 'faturamento'

    Retorna um novo DataFrame tratado.
    """
    df = df.copy()

    # remove duplicados exatos
    df = df.drop_duplicates()

    # normaliza nomes de colunas (espaços, maiúsculas)
    df.columns = [c.strip().lower() for c in df.columns]

    # converte data; datas inválidas viram NaT e são descartadas depois
    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    # converte quantidade e preco para numérico; inválidos viram NaN
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
    df["preco"] = pd.to_numeric(df["preco"], errors="coerce")

    # remove linhas sem informações essenciais
    df = df.dropna(subset=["data", "produto", "categoria", "quantidade", "preco"])

    # remove linhas com valores não positivos (inconsistentes para vendas)
    df = df[(df["quantidade"] > 0) & (df["preco"] > 0)]

    # normaliza texto
    df["produto"] = df["produto"].astype(str).str.strip()
    df["categoria"] = df["categoria"].astype(str).str.strip()

    # cria coluna de faturamento
    df["faturamento"] = df["quantidade"] * df["preco"]

    # cria colunas auxiliares de tempo, úteis para análises mensais
    df["ano_mes"] = df["data"].dt.to_period("M").astype(str)

    df = df.sort_values("data").reset_index(drop=True)

    return df
