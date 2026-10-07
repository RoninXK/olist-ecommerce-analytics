from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Olist Analytics",
    page_icon="🛒",
    layout="wide"
)

PASTA_PROJETO = Path(__file__).resolve().parent
PASTA_DADOS = PASTA_PROJETO / "data" / "processed"


# ============================================================
# CARREGAMENTO
# ============================================================

@st.cache_data
def carregar_dados():

    pedidos = pd.read_csv(
        PASTA_DADOS / "olist_orders_analytics.csv"
    )

    itens = pd.read_csv(
        PASTA_DADOS / "olist_items_analytics.csv"
    )

    pagamentos = pd.read_csv(
        PASTA_DADOS / "olist_payments.csv"
    )

    pedidos["order_purchase_timestamp"] = pd.to_datetime(
        pedidos["order_purchase_timestamp"],
        errors="coerce"
    )

    itens["order_purchase_timestamp"] = pd.to_datetime(
        itens["order_purchase_timestamp"],
        errors="coerce"
    )

    return pedidos, itens, pagamentos


pedidos, itens, pagamentos = carregar_dados()


# ============================================================
# FILTRAR PEDIDOS ENTREGUES
# ============================================================

pedidos_entregues = pedidos[
    pedidos["order_status"] == "delivered"
].copy()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🛒 Olist Analytics")

pagina = st.sidebar.radio(
    "Navegação",
    [
        "🏠 Visão Geral",
        "💰 Vendas",
        "📦 Produtos",
        "🚚 Logística",
        "💳 Pagamentos",
        "⭐ Clientes",
        "🔍 Insights"
    ]
)


st.sidebar.divider()

st.sidebar.subheader("Filtros")


# ============================================================
# FILTRO DE DATA
# ============================================================

data_minima = (
    pedidos_entregues["order_purchase_timestamp"]
    .min()
    .date()
)

data_maxima = (
    pedidos_entregues["order_purchase_timestamp"]
    .max()
    .date()
)


periodo = st.sidebar.date_input(
    "Período",
    value=(
        data_minima,
        data_maxima
    ),
    min_value=data_minima,
    max_value=data_maxima
)


# ============================================================
# FILTRO DE ESTADO
# ============================================================

estados = sorted(
    pedidos_entregues[
        "customer_state"
    ]
    .dropna()
    .unique()
)


estado = st.sidebar.multiselect(
    "Estado",
    estados,
    default=estados
)


# ============================================================
# APLICAR FILTROS
# ============================================================

dados = pedidos_entregues.copy()


if len(periodo) == 2:

    inicio = pd.Timestamp(
        periodo[0]
    )

    fim = (
        pd.Timestamp(periodo[1])
        + pd.Timedelta(days=1)
    )

    dados = dados[
        (
            dados[
                "order_purchase_timestamp"
            ] >= inicio
        )
        &
        (
            dados[
                "order_purchase_timestamp"
            ] < fim
        )
    ]


dados = dados[
    dados["customer_state"].isin(
        estado
    )
]


ids_filtrados = set(
    dados["order_id"]
)


itens_filtrados = itens[
    itens["order_id"].isin(
        ids_filtrados
    )
].copy()


# ============================================================
# CABEÇALHO
# ============================================================

st.title("🛒 Olist E-Commerce Analytics")

st.caption(
    "Dashboard de análise de vendas, clientes, produtos e logística."
)


# ============================================================
# VISÃO GERAL
# ============================================================

if pagina == "🏠 Visão Geral":

    st.header("Visão Geral do Negócio")

    faturamento = (
        dados["payment_total"]
        .fillna(0)
        .sum()
    )

    pedidos_total = (
        dados["order_id"]
        .nunique()
    )

    clientes = (
        dados["customer_unique_id"]
        .nunique()
    )

    itens_total = len(
        itens_filtrados
    )

    ticket_medio = (
        faturamento / pedidos_total
        if pedidos_total > 0
        else 0
    )


    coluna1, coluna2, coluna3, coluna4, coluna5 = st.columns(5)

    coluna1.metric(
        "Faturamento",
        f"R$ {faturamento:,.2f}"
    )

    coluna2.metric(
        "Pedidos",
        f"{pedidos_total:,}"
    )

    coluna3.metric(
        "Ticket Médio",
        f"R$ {ticket_medio:,.2f}"
    )

    coluna4.metric(
        "Clientes",
        f"{clientes:,}"
    )

    coluna5.metric(
        "Itens vendidos",
        f"{itens_total:,}"
    )


    st.divider()


    # --------------------------------------------------------
    # VENDAS POR MÊS
    # --------------------------------------------------------

    dados["ano_mes"] = (
        dados[
            "order_purchase_timestamp"
        ]
        .dt.to_period("M")
        .astype(str)
    )


    mensal = (
        dados
        .groupby("ano_mes")
        .agg(
            faturamento=(
                "payment_total",
                "sum"
            ),

            pedidos=(
                "order_id",
                "nunique"
            )
        )
        .reset_index()
    )


    fig = px.line(
        mensal,
        x="ano_mes",
        y="faturamento",
        markers=True,
        title="Evolução do Faturamento"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # ESTADOS
    # --------------------------------------------------------

    vendas_estado = (
        dados
        .groupby("customer_state")
        ["payment_total"]
        .sum()
        .reset_index()
        .sort_values(
            "payment_total",
            ascending=False
        )
        .head(10)
    )


    fig = px.bar(
        vendas_estado,
        x="customer_state",
        y="payment_total",
        title="Top 10 Estados por Faturamento"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# VENDAS
# ============================================================

elif pagina == "💰 Vendas":

    st.header("Análise de Vendas")


    dados["ano_mes"] = (
        dados[
            "order_purchase_timestamp"
        ]
        .dt.to_period("M")
        .astype(str)
    )


    vendas = (
        dados
        .groupby("ano_mes")
        .agg(
            faturamento=(
                "payment_total",
                "sum"
            ),

            pedidos=(
                "order_id",
                "nunique"
            ),

            clientes=(
                "customer_unique_id",
                "nunique"
            )
        )
        .reset_index()
    )


    vendas["ticket_medio"] = (
        vendas["faturamento"]
        /
        vendas["pedidos"]
    )


    fig = px.line(
        vendas,
        x="ano_mes",
        y="faturamento",
        markers=True,
        title="Faturamento Mensal"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    fig = px.bar(
        vendas,
        x="ano_mes",
        y="pedidos",
        title="Pedidos por Mês"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.subheader("Dados mensais")

    st.dataframe(
        vendas,
        use_container_width=True
    )


# ============================================================
# PRODUTOS
# ============================================================

elif pagina == "📦 Produtos":

    st.header("Produtos e Categorias")


    categorias = (
        itens_filtrados
        .groupby("product_category")
        .agg(
            faturamento=(
                "price",
                "sum"
            ),

            itens_vendidos=(
                "order_item_id",
                "count"
            ),

            pedidos=(
                "order_id",
                "nunique"
            )
        )
        .reset_index()
        .sort_values(
            "faturamento",
            ascending=False
        )
    )


    top20 = categorias.head(20)


    fig = px.bar(
        top20,
        x="faturamento",
        y="product_category",
        orientation="h",
        title="Top 20 Categorias por Faturamento"
    )

    fig.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    fig = px.bar(
        categorias
        .sort_values(
            "itens_vendidos",
            ascending=False
        )
        .head(20),

        x="itens_vendidos",
        y="product_category",
        orientation="h",
        title="Categorias com Mais Itens Vendidos"
    )


    fig.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        }
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# LOGÍSTICA
# ============================================================

elif pagina == "🚚 Logística":

    st.header("Análise Logística")


    entregas = dados[
        dados["delivery_days"]
        .notna()
    ].copy()


    tempo_medio = (
        entregas["delivery_days"]
        .mean()
    )


    atrasados = (
        entregas[
            "delivery_difference_days"
        ] > 0
    ).mean() * 100


    frete_total = (
        itens_filtrados[
            "freight_value"
        ]
        .sum()
    )


    c1, c2, c3 = st.columns(3)


    c1.metric(
        "Tempo Médio de Entrega",
        f"{tempo_medio:.1f} dias"
    )


    c2.metric(
        "Pedidos Atrasados",
        f"{atrasados:.1f}%"
    )


    c3.metric(
        "Frete Total",
        f"R$ {frete_total:,.2f}"
    )


    logistica_estado = (
        entregas
        .groupby("customer_state")
        .agg(
            tempo_medio=(
                "delivery_days",
                "mean"
            ),

            atraso_medio=(
                "delivery_difference_days",
                "mean"
            )
        )
        .reset_index()
    )


    fig = px.bar(
        logistica_estado
        .sort_values(
            "tempo_medio",
            ascending=False
        ),

        x="customer_state",
        y="tempo_medio",
        title="Tempo Médio de Entrega por Estado"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PAGAMENTOS
# ============================================================

elif pagina == "💳 Pagamentos":

    st.header("Formas de Pagamento")


    pagamentos_filtrados = pagamentos[
        pagamentos["order_id"]
        .isin(ids_filtrados)
    ]


    resumo_pagamentos = (
        pagamentos_filtrados
        .groupby("payment_type")
        .agg(
            valor=(
                "payment_value",
                "sum"
            ),

            transacoes=(
                "order_id",
                "count"
            )
        )
        .reset_index()
    )


    fig = px.pie(
        resumo_pagamentos,
        names="payment_type",
        values="valor",
        title="Distribuição do Valor por Forma de Pagamento"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    parcelas = (
        pagamentos_filtrados[
            pagamentos_filtrados[
                "payment_installments"
            ] > 0
        ]
        .groupby(
            "payment_installments"
        )
        .size()
        .reset_index(
            name="quantidade"
        )
    )


    fig = px.bar(
        parcelas,
        x="payment_installments",
        y="quantidade",
        title="Quantidade de Compras por Número de Parcelas"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# CLIENTES
# ============================================================

elif pagina == "⭐ Clientes":

    st.header("Experiência do Cliente")


    avaliacoes = dados[
        dados["review_score"]
        .notna()
    ].copy()


    nota_media = (
        avaliacoes["review_score"]
        .mean()
    )


    st.metric(
        "Nota Média",
        f"{nota_media:.2f} / 5"
    )


    notas = (
        avaliacoes
        .groupby("review_score")
        .size()
        .reset_index(
            name="quantidade"
        )
    )


    fig = px.bar(
        notas,
        x="review_score",
        y="quantidade",
        title="Distribuição das Avaliações"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    avaliacoes["situacao"] = (
        avaliacoes[
            "delivery_difference_days"
        ]
        .apply(
            lambda x:
            "Atrasado"
            if x > 0
            else "No prazo"
        )
    )


    impacto_atraso = (
        avaliacoes
        .groupby("situacao")
        ["review_score"]
        .mean()
        .reset_index()
    )


    fig = px.bar(
        impacto_atraso,
        x="situacao",
        y="review_score",
        title="Impacto do Atraso na Avaliação"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# INSIGHTS
# ============================================================

elif pagina == "🔍 Insights":

    st.header("Principais Insights")


    faturamento_estado = (
        dados
        .groupby("customer_state")
        ["payment_total"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    categoria_top = (
        itens_filtrados
        .groupby("product_category")
        ["price"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    if not faturamento_estado.empty:

        melhor_estado = (
            faturamento_estado
            .index[0]
        )

        st.success(
            f"💰 O estado com maior faturamento "
            f"é {melhor_estado}."
        )


    if not categoria_top.empty:

        melhor_categoria = (
            categoria_top
            .index[0]
        )

        st.info(
            f"📦 A categoria com maior faturamento "
            f"é {melhor_categoria}."
        )


    dados_avaliacao = dados[
        dados["review_score"]
        .notna()
        &
        dados[
            "delivery_difference_days"
        ].notna()
    ]


    nota_atrasado = (
        dados_avaliacao[
            dados_avaliacao[
                "delivery_difference_days"
            ] > 0
        ]["review_score"]
        .mean()
    )


    nota_prazo = (
        dados_avaliacao[
            dados_avaliacao[
                "delivery_difference_days"
            ] <= 0
        ]["review_score"]
        .mean()
    )


    st.warning(
        f"🚚 Pedidos entregues no prazo possuem "
        f"nota média de {nota_prazo:.2f}, "
        f"enquanto pedidos atrasados possuem "
        f"nota média de {nota_atrasado:.2f}."
    )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "Projeto de portfólio desenvolvido com "
    "Python, Pandas, SQL, SQLite, Plotly e Streamlit."
)