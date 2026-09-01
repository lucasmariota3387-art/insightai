"""
Módulo de geração de gráficos do InsightAI.

Cada função retorna uma figura Matplotlib pronta para ser exibida
no Streamlit com st.pyplot(fig).
"""

import matplotlib.pyplot as plt
import pandas as pd


def grafico_faturamento_por_produto(faturamento_por_produto: pd.Series, top_n: int = 10):
    dados = faturamento_por_produto.head(top_n).sort_values()

    fig, ax = plt.subplots(figsize=(8, 5))
    dados.plot(kind="barh", ax=ax, color="#4C72B0")
    ax.set_title(f"Top {top_n} produtos por faturamento")
    ax.set_xlabel("Faturamento (R$)")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


def grafico_faturamento_por_categoria(faturamento_por_categoria: pd.Series):
    fig, ax = plt.subplots(figsize=(6, 6))
    faturamento_por_categoria.plot(
        kind="pie",
        ax=ax,
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.set_title("Faturamento por categoria")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


def grafico_evolucao_mensal(vendas_por_mes: pd.Series):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    vendas_por_mes.plot(kind="line", marker="o", ax=ax, color="#DD8452")
    ax.set_title("Evolução mensal do faturamento")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Faturamento (R$)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def grafico_quantidade_por_produto(df: pd.DataFrame, top_n: int = 10):
    dados = (
        df.groupby("produto")["quantidade"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    dados.plot(kind="barh", ax=ax, color="#55A868")
    ax.set_title(f"Top {top_n} produtos mais vendidos (quantidade)")
    ax.set_xlabel("Unidades vendidas")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig
