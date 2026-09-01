"""
Módulo de análise do InsightAI.

Responsável por calcular indicadores de negócio (faturamento total,
ticket médio, produto/categoria líderes, evolução mensal, etc.) e
gerar insights automáticos baseados em regras simples (sem IA).
"""

import pandas as pd


def formatar_moeda(valor: float) -> str:
    """
    Formata um número no padrão monetário brasileiro:
    milhar com ponto e decimal com vírgula.

    Exemplo: 1163792.52 -> "R$ 1.163.792,52"
    """
    valor_formatado = f"{valor:,.2f}"

    valor_formatado = (
        valor_formatado
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {valor_formatado}"


def formatar_numero(valor: float) -> str:
    """
    Formata um número inteiro no padrão brasileiro (milhar com ponto).

    Exemplo: 1420 -> "1.420"
    """
    return f"{int(valor):,}".replace(",", ".")


def calcular_indicadores(df: pd.DataFrame) -> dict:
    """
    Calcula os indicadores principais do dashboard.
    Retorna um dicionário com os valores agregados.
    """
    faturamento_total = df["faturamento"].sum()
    quantidade_total = df["quantidade"].sum()
    numero_vendas = len(df)
    ticket_medio = df["faturamento"].mean() if numero_vendas > 0 else 0

    faturamento_por_produto = (
        df.groupby("produto")["faturamento"].sum().sort_values(ascending=False)
    )
    faturamento_por_categoria = (
        df.groupby("categoria")["faturamento"].sum().sort_values(ascending=False)
    )
    vendas_por_mes = df.groupby("ano_mes")["faturamento"].sum().sort_index()

    produto_top = faturamento_por_produto.idxmax() if not faturamento_por_produto.empty else None
    categoria_top = faturamento_por_categoria.idxmax() if not faturamento_por_categoria.empty else None

    return {
        "faturamento_total": faturamento_total,
        "quantidade_total": quantidade_total,
        "numero_vendas": numero_vendas,
        "ticket_medio": ticket_medio,
        "faturamento_por_produto": faturamento_por_produto,
        "faturamento_por_categoria": faturamento_por_categoria,
        "vendas_por_mes": vendas_por_mes,
        "produto_top": produto_top,
        "categoria_top": categoria_top,
    }


def calcular_qualidade_dados(total_bruto: int, total_tratado: int) -> dict:
    """
    Calcula indicadores simples sobre a qualidade do arquivo enviado:
    quantos registros chegaram, quantos passaram no tratamento e a
    taxa de aproveitamento resultante.
    """
    removidos = total_bruto - total_tratado
    taxa_aproveitamento = (total_tratado / total_bruto * 100) if total_bruto > 0 else 0

    return {
        "registros_recebidos": total_bruto,
        "registros_validos": total_tratado,
        "registros_removidos": removidos,
        "taxa_aproveitamento": round(taxa_aproveitamento, 1),
    }


def calcular_crescimento_mensal(vendas_por_mes: pd.Series) -> float | None:
    """
    Calcula a variação percentual de faturamento entre o penúltimo
    e o último mês disponíveis. Retorna None se não houver dados
    suficientes (menos de 2 meses).
    """
    if len(vendas_por_mes) < 2:
        return None

    ultimo = vendas_por_mes.iloc[-1]
    penultimo = vendas_por_mes.iloc[-2]

    if penultimo == 0:
        return None

    crescimento = ((ultimo - penultimo) / penultimo) * 100
    return round(crescimento, 1)


def gerar_insights_automaticos(indicadores: dict) -> list:
    """
    Gera uma lista de frases de insight com base em regras simples
    (sem IA), a partir dos indicadores já calculados.
    """
    insights = []

    produto_top = indicadores.get("produto_top")
    categoria_top = indicadores.get("categoria_top")
    vendas_por_mes = indicadores.get("vendas_por_mes")

    if produto_top:
        insights.append(f"O produto com maior faturamento foi **{produto_top}**.")

    if categoria_top:
        insights.append(f"A categoria com melhor desempenho foi **{categoria_top}**.")

    if vendas_por_mes is not None and len(vendas_por_mes) > 0:
        mes_top = vendas_por_mes.idxmax()
        insights.append(f"O mês com maior faturamento foi **{mes_top}**.")

    crescimento = calcular_crescimento_mensal(vendas_por_mes) if vendas_por_mes is not None else None
    if crescimento is not None:
        direcao = "crescimento" if crescimento >= 0 else "queda"
        insights.append(
            f"O faturamento apresentou {direcao} de **{abs(crescimento)}%** "
            "em relação ao mês anterior."
        )

    return insights


def montar_resumo_para_ia(indicadores: dict) -> str:
    """
    Monta um texto estruturado e resumido com os indicadores já
    calculados por Pandas, pronto para ser enviado como contexto
    a um modelo de IA generativa (ver ETAPA 16 do guia do projeto).

    Importante: este texto contém apenas números já calculados —
    a IA deve interpretar, não recalcular nem inventar dados.
    """
    crescimento = calcular_crescimento_mensal(indicadores.get("vendas_por_mes"))
    crescimento_texto = f"{crescimento}%" if crescimento is not None else "dados insuficientes"

    resumo = f"""
Faturamento total: {formatar_moeda(indicadores['faturamento_total'])}
Quantidade total vendida: {indicadores['quantidade_total']}
Número de vendas: {indicadores['numero_vendas']}
Ticket médio: {formatar_moeda(indicadores['ticket_medio'])}
Produto com maior faturamento: {indicadores['produto_top']}
Categoria com maior faturamento: {indicadores['categoria_top']}
Crescimento em relação ao mês anterior: {crescimento_texto}
""".strip()

    return resumo
