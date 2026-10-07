from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_PROJETO = Path(__file__).resolve().parent.parent

PASTA_DADOS = (
    PASTA_PROJETO
    / "data"
    / "processed"
)

ARQUIVO_PEDIDOS = (
    PASTA_DADOS
    / "olist_orders_analytics.csv"
)

ARQUIVO_ITENS = (
    PASTA_DADOS
    / "olist_items_analytics.csv"
)


print("\n========================================")
print("OLIST ANALYTICS - INDICADORES")
print("========================================\n")


# ============================================================
# 1. CARREGAR DADOS
# ============================================================

print("1. Carregando bases processadas...")


pedidos = pd.read_csv(
    ARQUIVO_PEDIDOS
)

itens = pd.read_csv(
    ARQUIVO_ITENS
)


pedidos["order_purchase_timestamp"] = pd.to_datetime(
    pedidos["order_purchase_timestamp"],
    errors="coerce"
)

pedidos["order_delivered_customer_date"] = pd.to_datetime(
    pedidos["order_delivered_customer_date"],
    errors="coerce"
)

pedidos["order_estimated_delivery_date"] = pd.to_datetime(
    pedidos["order_estimated_delivery_date"],
    errors="coerce"
)

itens["order_purchase_timestamp"] = pd.to_datetime(
    itens["order_purchase_timestamp"],
    errors="coerce"
)


print(
    f"Pedidos carregados: {len(pedidos)}"
)

print(
    f"Itens carregados: {len(itens)}"
)


# ============================================================
# 2. FILTRAR PEDIDOS ENTREGUES
# ============================================================

print("\n2. Selecionando pedidos entregues...")


pedidos_entregues = pedidos[
    pedidos["order_status"] == "delivered"
].copy()


ids_entregues = set(
    pedidos_entregues["order_id"]
)


itens_entregues = itens[
    itens["order_id"].isin(ids_entregues)
].copy()


print(
    f"Pedidos entregues: "
    f"{len(pedidos_entregues)}"
)

print(
    f"Itens de pedidos entregues: "
    f"{len(itens_entregues)}"
)


# ============================================================
# 3. KPIs PRINCIPAIS
# ============================================================

print("\n3. Calculando KPIs...")


faturamento_total = (
    pedidos_entregues["payment_total"]
    .fillna(0)
    .sum()
)


total_pedidos = (
    pedidos_entregues["order_id"]
    .nunique()
)


ticket_medio = (
    faturamento_total
    / total_pedidos
)


clientes_unicos = (
    pedidos_entregues["customer_unique_id"]
    .nunique()
)


itens_vendidos = (
    len(itens_entregues)
)


valor_produtos = (
    itens_entregues["price"]
    .fillna(0)
    .sum()
)


frete_total = (
    itens_entregues["freight_value"]
    .fillna(0)
    .sum()
)


frete_medio_pedido = (
    frete_total
    / total_pedidos
)


nota_media = (
    pedidos_entregues["review_score"]
    .mean()
)


tempo_medio_entrega = (
    pedidos_entregues["delivery_days"]
    .dropna()
    .mean()
)


pedidos_com_entrega = pedidos_entregues[
    pedidos_entregues[
        "delivery_difference_days"
    ].notna()
]


percentual_atrasados = (
    pedidos_com_entrega["is_late"]
    .astype(bool)
    .mean()
    * 100
)


# ============================================================
# 4. EXIBIR KPIs
# ============================================================

print("\n========================================")
print("KPIs PRINCIPAIS")
print("========================================\n")


print(
    f"Faturamento total: "
    f"R$ {faturamento_total:,.2f}"
)

print(
    f"Pedidos entregues: "
    f"{total_pedidos:,}"
)

print(
    f"Ticket médio: "
    f"R$ {ticket_medio:,.2f}"
)

print(
    f"Clientes únicos: "
    f"{clientes_unicos:,}"
)

print(
    f"Itens vendidos: "
    f"{itens_vendidos:,}"
)

print(
    f"Valor dos produtos: "
    f"R$ {valor_produtos:,.2f}"
)

print(
    f"Frete total: "
    f"R$ {frete_total:,.2f}"
)

print(
    f"Frete médio por pedido: "
    f"R$ {frete_medio_pedido:,.2f}"
)

print(
    f"Nota média: "
    f"{nota_media:.2f}"
)

print(
    f"Tempo médio de entrega: "
    f"{tempo_medio_entrega:.2f} dias"
)

print(
    f"Pedidos atrasados: "
    f"{percentual_atrasados:.2f}%"
)


# ============================================================
# 5. SALVAR KPIs
# ============================================================

kpis = pd.DataFrame({
    "Indicador": [
        "Faturamento Total",
        "Pedidos Entregues",
        "Ticket Medio",
        "Clientes Unicos",
        "Itens Vendidos",
        "Valor Produtos",
        "Frete Total",
        "Frete Medio Pedido",
        "Nota Media",
        "Tempo Medio Entrega",
        "Percentual Atrasados",
    ],

    "Valor": [
        faturamento_total,
        total_pedidos,
        ticket_medio,
        clientes_unicos,
        itens_vendidos,
        valor_produtos,
        frete_total,
        frete_medio_pedido,
        nota_media,
        tempo_medio_entrega,
        percentual_atrasados,
    ]
})


kpis.to_csv(
    PASTA_DADOS / "kpis.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 6. VENDAS POR MÊS
# ============================================================

print("\n4. Calculando vendas por mês...")


pedidos_entregues["ano_mes"] = (
    pedidos_entregues[
        "order_purchase_timestamp"
    ]
    .dt.to_period("M")
    .astype(str)
)


vendas_mes = (
    pedidos_entregues
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
        ),
    )
    .reset_index()
)


vendas_mes["ticket_medio"] = (
    vendas_mes["faturamento"]
    / vendas_mes["pedidos"]
)


vendas_mes.to_csv(
    PASTA_DADOS / "vendas_por_mes.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 7. VENDAS POR ESTADO
# ============================================================

print("5. Calculando vendas por estado...")


vendas_estado = (
    pedidos_entregues
    .groupby("customer_state")
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
        ),
    )
    .reset_index()
)


vendas_estado["ticket_medio"] = (
    vendas_estado["faturamento"]
    / vendas_estado["pedidos"]
)


vendas_estado = vendas_estado.sort_values(
    by="faturamento",
    ascending=False
)


vendas_estado.to_csv(
    PASTA_DADOS / "vendas_por_estado.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 8. CATEGORIAS
# ============================================================

print("6. Calculando desempenho das categorias...")


categorias = (
    itens_entregues
    .groupby("product_category")
    .agg(
        itens_vendidos=(
            "order_item_id",
            "count"
        ),

        faturamento_produtos=(
            "price",
            "sum"
        ),

        frete=(
            "freight_value",
            "sum"
        ),

        pedidos=(
            "order_id",
            "nunique"
        ),
    )
    .reset_index()
)


categorias["preco_medio"] = (
    categorias["faturamento_produtos"]
    / categorias["itens_vendidos"]
)


categorias = categorias.sort_values(
    by="faturamento_produtos",
    ascending=False
)


categorias.to_csv(
    PASTA_DADOS / "categorias.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 9. FORMAS DE PAGAMENTO
# ============================================================

print("7. Calculando formas de pagamento...")


pagamentos = (
    pedidos_entregues
    .groupby("payment_type")
    .agg(
        pedidos=(
            "order_id",
            "nunique"
        ),

        faturamento=(
            "payment_total",
            "sum"
        ),

        parcelas_media=(
            "max_installments",
            "mean"
        ),
    )
    .reset_index()
)


pagamentos["percentual_pedidos"] = (
    pagamentos["pedidos"]
    / total_pedidos
    * 100
)


pagamentos = pagamentos.sort_values(
    by="pedidos",
    ascending=False
)


pagamentos.to_csv(
    PASTA_DADOS / "formas_pagamento.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 10. ENTREGA POR ESTADO
# ============================================================

print("8. Calculando entregas por estado...")


entregas_estado = (
    pedidos_com_entrega
    .groupby("customer_state")
    .agg(
        pedidos=(
            "order_id",
            "nunique"
        ),

        tempo_medio_entrega=(
            "delivery_days",
            "mean"
        ),

        atraso_medio=(
            "delivery_difference_days",
            "mean"
        ),

        percentual_atrasados=(
            "is_late",
            "mean"
        ),
    )
    .reset_index()
)


entregas_estado["percentual_atrasados"] = (
    entregas_estado["percentual_atrasados"]
    * 100
)


entregas_estado = entregas_estado.sort_values(
    by="tempo_medio_entrega",
    ascending=False
)


entregas_estado.to_csv(
    PASTA_DADOS / "entregas_por_estado.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 11. AVALIAÇÃO X ATRASO
# ============================================================

print("9. Calculando relação entre atraso e avaliação...")


avaliacao_atraso = (
    pedidos_com_entrega[
        pedidos_com_entrega[
            "review_score"
        ].notna()
    ]
    .groupby("is_late")
    .agg(
        pedidos=(
            "order_id",
            "nunique"
        ),

        nota_media=(
            "review_score",
            "mean"
        ),
    )
    .reset_index()
)


avaliacao_atraso["situacao"] = (
    avaliacao_atraso["is_late"]
    .map({
        False: "No prazo",
        True: "Atrasado"
    })
)


avaliacao_atraso.to_csv(
    PASTA_DADOS
    / "avaliacao_atraso.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 12. STATUS DOS PEDIDOS
# ============================================================

print("10. Calculando status dos pedidos...")


status_pedidos = (
    pedidos
    .groupby("order_status")
    .size()
    .reset_index(
        name="quantidade"
    )
)


status_pedidos["percentual"] = (
    status_pedidos["quantidade"]
    / len(pedidos)
    * 100
)


status_pedidos = status_pedidos.sort_values(
    by="quantidade",
    ascending=False
)


status_pedidos.to_csv(
    PASTA_DADOS
    / "status_pedidos.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 13. TOP CATEGORIAS
# ============================================================

print("\n========================================")
print("TOP 10 CATEGORIAS POR FATURAMENTO")
print("========================================\n")


print(
    categorias[
        [
            "product_category",
            "faturamento_produtos",
            "itens_vendidos"
        ]
    ]
    .head(10)
    .to_string(
        index=False
    )
)


# ============================================================
# 14. TOP ESTADOS
# ============================================================

print("\n========================================")
print("TOP 10 ESTADOS POR FATURAMENTO")
print("========================================\n")


print(
    vendas_estado[
        [
            "customer_state",
            "faturamento",
            "pedidos"
        ]
    ]
    .head(10)
    .to_string(
        index=False
    )
)


# ============================================================
# FINAL
# ============================================================

print("\n========================================")
print("ANÁLISE CONCLUÍDA")
print("========================================\n")


print("Arquivos gerados:")

print(" - kpis.csv")
print(" - vendas_por_mes.csv")
print(" - vendas_por_estado.csv")
print(" - categorias.csv")
print(" - formas_pagamento.csv")
print(" - entregas_por_estado.csv")
print(" - avaliacao_atraso.csv")
print(" - status_pedidos.csv")