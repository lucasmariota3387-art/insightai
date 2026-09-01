"""
InsightAI — Dashboard Inteligente de Análise de Dados de Vendas

Aplicação Streamlit que recebe um arquivo CSV de vendas, trata os
dados com Pandas, calcula indicadores de negócio, exibe visualizações
com Matplotlib e gera insights automáticos.
"""

import pandas as pd
import streamlit as st

from src.tratamento import tratar_dados, validar_colunas
from src.analise import (
    calcular_indicadores,
    gerar_insights_automaticos,
    montar_resumo_para_ia,
    calcular_qualidade_dados,
    formatar_moeda,
    formatar_numero,
)
from src.graficos import (
    grafico_faturamento_por_produto,
    grafico_faturamento_por_categoria,
    grafico_evolucao_mensal,
    grafico_quantidade_por_produto,
)

st.set_page_config(
    page_title="InsightAI",
    page_icon="📊",
    layout="wide",
)

st.title("📊 InsightAI")
st.caption("Análise inteligente de vendas")
st.write(
    "Transforme seus dados de vendas em informações estratégicas. "
    "Envie um arquivo CSV e receba automaticamente indicadores, "
    "visualizações, filtros e insights."
)

with st.expander("Formato esperado do arquivo CSV"):
    st.code("data,produto,categoria,quantidade,preco", language="text")
    st.caption(
        "Colunas obrigatórias: data (AAAA-MM-DD), produto, categoria, "
        "quantidade (número) e preco (número)."
    )

# ---------------------------------------------------------------------
# 1. Upload do arquivo
# ---------------------------------------------------------------------
uploaded_file = st.file_uploader("Envie seu arquivo CSV de vendas", type=["csv"])

usar_exemplo = False
if uploaded_file is None:
    usar_exemplo = st.checkbox("Usar dados de exemplo (dados/vendas.csv)", value=True)

df_bruto = None

if uploaded_file is not None:
    try:
        df_bruto = pd.read_csv(uploaded_file)
    except Exception:
        st.error("Não foi possível processar o arquivo. Verifique se é um CSV válido.")
elif usar_exemplo:
    try:
        df_bruto = pd.read_csv("dados/vendas.csv")
    except Exception:
        st.error("Não foi possível carregar o arquivo de exemplo.")

if df_bruto is None:
    st.info("Envie um arquivo CSV ou marque a opção de usar os dados de exemplo para começar.")
    st.stop()

# ---------------------------------------------------------------------
# 2. Validação das colunas
# ---------------------------------------------------------------------
colunas_faltando = validar_colunas(df_bruto)
if colunas_faltando:
    st.error(
        "O arquivo não possui todas as colunas necessárias. "
        f"Colunas faltando: {', '.join(colunas_faltando)}"
    )
    st.stop()

with st.expander("Prévia dos dados originais"):
    st.dataframe(df_bruto.head(10))
    st.caption(f"{len(df_bruto)} linhas carregadas antes do tratamento.")

# ---------------------------------------------------------------------
# 3. Tratamento dos dados
# ---------------------------------------------------------------------
df = tratar_dados(df_bruto)

if df.empty:
    st.error("Após o tratamento, não restaram dados válidos para análise.")
    st.stop()

qualidade = calcular_qualidade_dados(len(df_bruto), len(df))

if qualidade["registros_removidos"] > 0:
    st.warning(
        f"{qualidade['registros_removidos']} linha(s) foram removidas por dados "
        "inválidos, ausentes ou duplicados. Veja detalhes em 'Qualidade dos dados' abaixo."
    )

st.subheader("Qualidade dos dados")
qcol1, qcol2, qcol3, qcol4 = st.columns(4)
qcol1.metric("Registros recebidos", formatar_numero(qualidade["registros_recebidos"]))
qcol2.metric("Registros válidos", formatar_numero(qualidade["registros_validos"]))
qcol3.metric("Registros removidos", formatar_numero(qualidade["registros_removidos"]))
qcol4.metric("Taxa de aproveitamento", f"{qualidade['taxa_aproveitamento']:.1f}%".replace(".", ","))

st.divider()

# ---------------------------------------------------------------------
# 4. Filtros
# ---------------------------------------------------------------------
st.sidebar.header("Filtros")

categorias_disponiveis = sorted(df["categoria"].unique())
categorias_selecionadas = st.sidebar.multiselect(
    "Categoria", categorias_disponiveis, default=categorias_disponiveis
)

produtos_disponiveis = sorted(df["produto"].unique())
produtos_selecionados = st.sidebar.multiselect(
    "Produto", produtos_disponiveis, default=produtos_disponiveis
)

data_min = df["data"].min().date()
data_max = df["data"].max().date()
periodo = st.sidebar.date_input(
    "Período", value=(data_min, data_max), min_value=data_min, max_value=data_max
)

df_filtrado = df[
    df["categoria"].isin(categorias_selecionadas)
    & df["produto"].isin(produtos_selecionados)
]

if isinstance(periodo, tuple) and len(periodo) == 2:
    inicio, fim = periodo
    df_filtrado = df_filtrado[
        (df_filtrado["data"].dt.date >= inicio) & (df_filtrado["data"].dt.date <= fim)
    ]

if df_filtrado.empty:
    st.warning("Nenhum dado corresponde aos filtros selecionados.")
    st.stop()

# ---------------------------------------------------------------------
# 5. Indicadores (cards)
# ---------------------------------------------------------------------
indicadores = calcular_indicadores(df_filtrado)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento total", formatar_moeda(indicadores["faturamento_total"]))
col2.metric("Nº de vendas", formatar_numero(indicadores["numero_vendas"]))
col3.metric("Itens vendidos", formatar_numero(indicadores["quantidade_total"]))
col4.metric("Ticket médio", formatar_moeda(indicadores["ticket_medio"]))

st.divider()

# ---------------------------------------------------------------------
# 6. Gráficos
# ---------------------------------------------------------------------
st.subheader("Visualizações")

linha1_col1, linha1_col2 = st.columns(2)
with linha1_col1:
    st.pyplot(grafico_faturamento_por_produto(indicadores["faturamento_por_produto"]))
with linha1_col2:
    st.pyplot(grafico_faturamento_por_categoria(indicadores["faturamento_por_categoria"]))

linha2_col1, linha2_col2 = st.columns(2)
with linha2_col1:
    st.pyplot(grafico_evolucao_mensal(indicadores["vendas_por_mes"]))
with linha2_col2:
    st.pyplot(grafico_quantidade_por_produto(df_filtrado))

st.divider()

# ---------------------------------------------------------------------
# 7. Insights automáticos (baseados em regras)
# ---------------------------------------------------------------------
st.subheader("Insights")

insights = gerar_insights_automaticos(indicadores)
for insight in insights:
    st.write(f"- {insight}")

with st.expander("Resumo estruturado (pronto para envio a uma IA generativa)"):
    st.code(montar_resumo_para_ia(indicadores), language="text")
    st.caption(
        "Este resumo pode ser enviado como contexto a um modelo de IA para "
        "gerar uma análise executiva em linguagem natural. Os insights "
        "gerados por IA devem se basear exclusivamente nestes indicadores "
        "e são um apoio à interpretação, não um substituto da análise humana."
    )

st.divider()

# ---------------------------------------------------------------------
# 8. Tabela de dados tratados
# ---------------------------------------------------------------------
with st.expander("Ver dados tratados"):
    st.dataframe(df_filtrado)

st.caption("InsightAI — projeto de portfólio construído com Python, Pandas, Matplotlib e Streamlit.")
