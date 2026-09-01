# InsightAI

Dashboard inteligente para análise automatizada de dados comerciais.

## Sobre o projeto

Pequenos negócios armazenam informações comerciais em planilhas, mas muitas vezes não dispõem de ferramentas ou conhecimento técnico para transformar esses dados em informações estratégicas. O InsightAI automatiza esse processo por meio de análise de dados e visualizações interativas, permitindo que qualquer pessoa envie um arquivo CSV de vendas e receba, em segundos, um panorama completo do negócio.

## Problema

- Quanto a empresa vendeu?
- Qual produto vende mais?
- Qual categoria gera mais receita?
- Qual mês teve o melhor resultado?
- O faturamento está crescendo ou caindo?

## Solução

Uma aplicação web que recebe um CSV de vendas e devolve, automaticamente:

- indicadores de negócio (faturamento total, ticket médio, nº de vendas);
- visualizações de produtos e categorias mais rentáveis;
- evolução mensal do faturamento;
- filtros por categoria, produto e período;
- insights automáticos gerados a partir dos dados (com possibilidade de expansão futura via IA generativa).

### O que conta como uma "venda"

Cada linha do arquivo CSV representa uma **transação de venda**, podendo conter uma ou mais unidades do mesmo produto (ver coluna `quantidade`). É essa premissa que sustenta o cálculo de `numero_vendas` (uma linha = uma venda) e do `ticket_medio` (faturamento médio por transação).

Em uma versão futura, essa regra pode ser refinada com uma coluna `id_venda`, permitindo agrupar múltiplos itens dentro de um mesmo pedido e calcular o ticket médio por pedido (não por linha).

## Funcionalidades

- Upload de arquivo CSV
- Validação das colunas obrigatórias (aceita cabeçalhos com variação de espaços e maiúsculas/minúsculas, ex.: `Produto`, ` PRODUTO`, `produto `)
- Tratamento e limpeza automática dos dados (duplicados, valores ausentes, tipos inválidos, preços/quantidades não positivos)
- Card de qualidade dos dados (registros recebidos, válidos, removidos e taxa de aproveitamento)
- Cards com métricas principais, com valores monetários no padrão brasileiro (ex.: `R$ 1.163.792,52`)
- 4 visualizações de dados (produtos, categorias, evolução mensal, quantidade vendida) — dashboard interativo no sentido de filtros e navegação; os gráficos em si são estáticos (Matplotlib)
- Filtros por categoria, produto e período
- Geração de insights automáticos baseados em regras
- Resumo estruturado pronto para ser enviado a um modelo de IA generativa

## Tecnologias utilizadas

- Python
- Pandas
- Matplotlib
- Streamlit
- Git / GitHub
- IA Generativa (etapa de expansão)

## Arquitetura

```text
              USUÁRIO
                 │
                 ▼
           STREAMLIT UI
                 │
                 ▼
              CSV
                 │
                 ▼
              PANDAS
          ┌──────┴──────┐
          ▼             ▼
      LIMPEZA        ANÁLISE
          │             │
          └──────┬──────┘
                 ▼
             MÉTRICAS
          ┌──────┴──────┐
          ▼             ▼
      GRÁFICOS       INSIGHTS
          │             │
          └──────┬──────┘
                 ▼
            DASHBOARD
```

## Estrutura do projeto

```text
InsightAI/
│
├── app.py
├── dados/
│   └── vendas.csv
│
├── src/
│   ├── tratamento.py
│   ├── analise.py
│   └── graficos.py
│
├── screenshots/
├── README.md
├── requirements.txt
└── .gitignore
```

## Como executar

1. Clone o repositório e entre na pasta do projeto.
2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação:

   ```bash
   streamlit run app.py
   ```

5. O navegador abrirá automaticamente em `http://localhost:8501`. Envie seu próprio CSV ou use os dados de exemplo (`dados/vendas.csv`) marcando a opção correspondente na tela inicial.

### Formato esperado do CSV

```csv
data,produto,categoria,quantidade,preco
2026-01-05,Notebook,Eletronicos,2,2500
2026-01-06,Mouse,Acessorios,5,80
```

## Qualidade dos dados

Após o upload, a aplicação exibe um card com o resultado do tratamento:

```text
QUALIDADE DOS DADOS

Registros recebidos        404
Registros válidos          400
Registros removidos          4
Taxa de aproveitamento    99,0%
```

O cálculo é feito por `calcular_qualidade_dados()` (`src/analise.py`):

```python
taxa_aproveitamento = (len(df) / len(df_bruto)) * 100
```

Isso torna visível — e não apenas implícito — quantos registros do arquivo original eram, de fato, utilizáveis.

## Segurança e privacidade

- Apenas arquivos `.csv` são aceitos pelo upload.
- As colunas obrigatórias são validadas antes de qualquer processamento.
- Os dados enviados são processados apenas em memória, durante a sessão, e não são armazenados permanentemente pela aplicação.
- Nenhuma chave de API é exposta no código-fonte; credenciais devem ser configuradas via variáveis de ambiente / `st.secrets`, e o arquivo `.env` é ignorado pelo Git (`.gitignore`).
- O carregamento do arquivo é protegido por tratamento de erros (`try/except`), evitando que a aplicação quebre diante de arquivos malformados.

## Screenshots

_Adicione aqui capturas de tela do dashboard após a primeira execução (`screenshots/dashboard.png`, `screenshots/upload.png`, `screenshots/analise.png`)._

## Roadmap

```text
v0.1  Leitura de CSV
v0.2  Tratamento de dados
v0.3  Dashboard
v0.4  Filtros
v0.5  Insights automáticos (regras)
v1.0  Versão pública
v1.1  IA generativa
v1.2  Migração de Matplotlib para Plotly (gráficos realmente interativos: zoom, hover, seleção)
v1.3  Exportação de relatório
v1.4  Novos tipos de dados
```

### Sobre a etapa de IA generativa (v1.1)

Os insights gerados por IA serão baseados exclusivamente nos indicadores já calculados pela aplicação (ver `src/analise.py::montar_resumo_para_ia`) e devem ser tratados como apoio à interpretação, não como substituto da análise humana. Nenhuma informação fora dos dados fornecidos deve ser inventada pelo modelo.

## Versionamento

Use commits pequenos e descritivos, seguindo o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: implementa dashboard inicial do InsightAI"

git add .
git commit -m "fix: corrige validacao de cabecalhos e adiciona qualidade dos dados"

git add .
git commit -m "docs: atualiza README com regras de negocio e screenshots"
```

Antes de cada `git push`, confira que nada sensível será versionado:

```bash
git status
```

Os seguintes itens **nunca** devem aparecer na saída (e já estão listados em `.gitignore`):

```text
.env
.streamlit/secrets.toml
.venv/
```

Lucas Ribeiro

GitHub: https://github.com/lucasmariota3387-art