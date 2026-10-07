from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_RAW = PASTA_PROJETO / "data" / "raw"
PASTA_PROCESSED = PASTA_PROJETO / "data" / "processed"

PASTA_PROCESSED.mkdir(
    parents=True,
    exist_ok=True
)


print("\n========================================")
print("OLIST ANALYTICS - TRATAMENTO DOS DADOS")
print("========================================\n")


# ============================================================
# 1. CARREGAR ARQUIVOS
# ============================================================

print("1. Carregando datasets...")


customers = pd.read_csv(
    PASTA_RAW / "olist_customers_dataset.csv"
)

orders = pd.read_csv(
    PASTA_RAW / "olist_orders_dataset.csv"
)

items = pd.read_csv(
    PASTA_RAW / "olist_order_items_dataset.csv"
)

payments = pd.read_csv(
    PASTA_RAW / "olist_order_payments_dataset.csv"
)

products = pd.read_csv(
    PASTA_RAW / "olist_products_dataset.csv"
)

sellers = pd.read_csv(
    PASTA_RAW / "olist_sellers_dataset.csv"
)

reviews = pd.read_csv(
    PASTA_RAW / "olist_order_reviews_dataset.csv"
)

translation = pd.read_csv(
    PASTA_RAW / "product_category_name_translation.csv"
)


print("Datasets carregados com sucesso.")


# ============================================================
# 2. CONVERTER DATAS
# ============================================================

print("\n2. Convertendo datas...")


colunas_datas_orders = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


for coluna in colunas_datas_orders:

    orders[coluna] = pd.to_datetime(
        orders[coluna],
        errors="coerce"
    )


items["shipping_limit_date"] = pd.to_datetime(
    items["shipping_limit_date"],
    errors="coerce"
)


reviews["review_creation_date"] = pd.to_datetime(
    reviews["review_creation_date"],
    errors="coerce"
)

reviews["review_answer_timestamp"] = pd.to_datetime(
    reviews["review_answer_timestamp"],
    errors="coerce"
)


print("Datas convertidas.")


# ============================================================
# 3. TRATAR PRODUTOS E TRADUZIR CATEGORIAS
# ============================================================

print("\n3. Tratando categorias de produtos...")


products = products.merge(
    translation,
    on="product_category_name",
    how="left"
)


products["product_category"] = (
    products["product_category_name_english"]
    .fillna(products["product_category_name"])
    .fillna("unknown")
)


print("Categorias tratadas.")


# ============================================================
# 4. AGREGAR ITENS POR PEDIDO
# ============================================================

print("\n4. Calculando valores dos pedidos...")


items["item_total"] = (
    items["price"]
    +
    items["freight_value"]
)


order_items_summary = (
    items
    .groupby("order_id")
    .agg(
        items_count=("order_item_id", "count"),
        products_value=("price", "sum"),
        freight_value=("freight_value", "sum"),
        order_items_value=("item_total", "sum"),
    )
    .reset_index()
)


print(
    f"Pedidos com itens: "
    f"{len(order_items_summary)}"
)


# ============================================================
# 5. AGREGAR PAGAMENTOS POR PEDIDO
# ============================================================

print("\n5. Tratando pagamentos...")


payments_summary = (
    payments
    .groupby("order_id")
    .agg(
        payment_total=("payment_value", "sum"),
        payment_records=("payment_sequential", "count"),
        max_installments=("payment_installments", "max"),
    )
    .reset_index()
)


# Forma de pagamento principal do pedido
payment_main = (
    payments
    .sort_values(
        ["order_id", "payment_value"],
        ascending=[True, False]
    )
    .drop_duplicates(
        subset="order_id",
        keep="first"
    )[
        [
            "order_id",
            "payment_type"
        ]
    ]
)


payments_summary = payments_summary.merge(
    payment_main,
    on="order_id",
    how="left"
)


print(
    f"Pedidos com pagamento: "
    f"{len(payments_summary)}"
)


# ============================================================
# 6. TRATAR AVALIAÇÕES
# ============================================================

print("\n6. Tratando avaliações...")


reviews_summary = (
    reviews
    .sort_values(
        "review_creation_date"
    )
    .drop_duplicates(
        subset="order_id",
        keep="last"
    )[
        [
            "order_id",
            "review_score",
            "review_creation_date"
        ]
    ]
)


print(
    f"Pedidos com avaliação: "
    f"{len(reviews_summary)}"
)


# ============================================================
# 7. CRIAR BASE DE PEDIDOS
# ============================================================

print("\n7. Criando base analítica de pedidos...")


orders_analytics = orders.merge(
    customers,
    on="customer_id",
    how="left"
)


orders_analytics = orders_analytics.merge(
    order_items_summary,
    on="order_id",
    how="left"
)


orders_analytics = orders_analytics.merge(
    payments_summary,
    on="order_id",
    how="left"
)


orders_analytics = orders_analytics.merge(
    reviews_summary,
    on="order_id",
    how="left"
)


# ============================================================
# 8. CRIAR MÉTRICAS DE ENTREGA
# ============================================================

print("\n8. Criando métricas de entrega...")


orders_analytics["delivery_days"] = (
    orders_analytics[
        "order_delivered_customer_date"
    ]
    -
    orders_analytics[
        "order_purchase_timestamp"
    ]
).dt.total_seconds() / 86400


orders_analytics["delivery_difference_days"] = (
    orders_analytics[
        "order_delivered_customer_date"
    ]
    -
    orders_analytics[
        "order_estimated_delivery_date"
    ]
).dt.total_seconds() / 86400


orders_analytics["is_late"] = (
    orders_analytics[
        "delivery_difference_days"
    ] > 0
)


# ============================================================
# 9. CRIAR COLUNAS DE DATA
# ============================================================

orders_analytics["purchase_year"] = (
    orders_analytics[
        "order_purchase_timestamp"
    ]
    .dt.year
)


orders_analytics["purchase_month"] = (
    orders_analytics[
        "order_purchase_timestamp"
    ]
    .dt.month
)


orders_analytics["purchase_year_month"] = (
    orders_analytics[
        "order_purchase_timestamp"
    ]
    .dt.to_period("M")
    .astype(str)
)


orders_analytics["purchase_weekday"] = (
    orders_analytics[
        "order_purchase_timestamp"
    ]
    .dt.day_name()
)


# ============================================================
# 10. CRIAR BASE ANALÍTICA DE ITENS
# ============================================================

print("\n9. Criando base analítica de itens...")


items_analytics = items.merge(
    products[
        [
            "product_id",
            "product_category",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ]
    ],
    on="product_id",
    how="left"
)


items_analytics = items_analytics.merge(
    sellers,
    on="seller_id",
    how="left"
)


items_analytics = items_analytics.merge(
    orders[
        [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
        ]
    ],
    on="order_id",
    how="left"
)


items_analytics = items_analytics.merge(
    customers[
        [
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state",
        ]
    ],
    on="customer_id",
    how="left"
)


# ============================================================
# 11. VALIDAÇÕES
# ============================================================

print("\n10. Executando validações...")


print(
    f"Pedidos originais: {len(orders)}"
)

print(
    f"Pedidos na base analítica: "
    f"{len(orders_analytics)}"
)

print(
    f"Itens originais: {len(items)}"
)

print(
    f"Itens na base analítica: "
    f"{len(items_analytics)}"
)


duplicados_pedidos = (
    orders_analytics["order_id"]
    .duplicated()
    .sum()
)


print(
    f"Pedidos duplicados na base final: "
    f"{duplicados_pedidos}"
)


print(
    "Valores nulos em customer_state: "
    f"{orders_analytics['customer_state'].isna().sum()}"
)


print(
    "Valores nulos em payment_total: "
    f"{orders_analytics['payment_total'].isna().sum()}"
)


# ============================================================
# 12. SALVAR ARQUIVOS
# ============================================================

print("\n11. Salvando datasets processados...")


ARQUIVO_ORDERS = (
    PASTA_PROCESSED
    / "olist_orders_analytics.csv"
)


ARQUIVO_ITEMS = (
    PASTA_PROCESSED
    / "olist_items_analytics.csv"
)


ARQUIVO_PAYMENTS = (
    PASTA_PROCESSED
    / "olist_payments.csv"
)


orders_analytics.to_csv(
    ARQUIVO_ORDERS,
    index=False,
    encoding="utf-8-sig"
)


items_analytics.to_csv(
    ARQUIVO_ITEMS,
    index=False,
    encoding="utf-8-sig"
)


payments.to_csv(
    ARQUIVO_PAYMENTS,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# RESULTADO FINAL
# ============================================================

print("\n========================================")
print("TRATAMENTO CONCLUÍDO")
print("========================================\n")


print(
    f"Base de pedidos: "
    f"{len(orders_analytics)} linhas"
)

print(
    f"Base de itens: "
    f"{len(items_analytics)} linhas"
)


print("\nArquivos criados:")

print(
    " - olist_orders_analytics.csv"
)

print(
    " - olist_items_analytics.csv"
)

print(
    " - olist_payments.csv"
)


print("\nPrimeiras linhas da base de pedidos:\n")

print(
    orders_analytics.head()
)