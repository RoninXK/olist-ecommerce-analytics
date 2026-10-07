from pathlib import Path
import sqlite3
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

ARQUIVO_BANCO = (
    PASTA_DADOS
    / "olist_analytics.db"
)


print("\n========================================")
print("OLIST ANALYTICS - BANCO SQLITE")
print("========================================\n")


# ============================================================
# 1. CARREGAR BASES PROCESSADAS
# ============================================================

print("1. Carregando arquivos processados...")


pedidos = pd.read_csv(
    PASTA_DADOS
    / "olist_orders_analytics.csv"
)

itens = pd.read_csv(
    PASTA_DADOS
    / "olist_items_analytics.csv"
)

pagamentos = pd.read_csv(
    PASTA_DADOS
    / "olist_payments.csv"
)


print(
    f"Pedidos: {len(pedidos)}"
)

print(
    f"Itens: {len(itens)}"
)

print(
    f"Pagamentos: {len(pagamentos)}"
)


# ============================================================
# 2. RECRIAR BANCO
# ============================================================

if ARQUIVO_BANCO.exists():

    ARQUIVO_BANCO.unlink()

    print(
        "\nBanco anterior removido."
    )


# ============================================================
# 3. CRIAR CONEXÃO
# ============================================================

conexao = sqlite3.connect(
    ARQUIVO_BANCO
)


print(
    "\n2. Banco SQLite criado."
)


# ============================================================
# 4. CRIAR TABELAS
# ============================================================

print(
    "\n3. Criando tabelas..."
)


pedidos.to_sql(
    "orders",
    conexao,
    if_exists="replace",
    index=False
)


itens.to_sql(
    "order_items",
    conexao,
    if_exists="replace",
    index=False
)


pagamentos.to_sql(
    "payments",
    conexao,
    if_exists="replace",
    index=False
)


print(
    "Tabela orders criada."
)

print(
    "Tabela order_items criada."
)

print(
    "Tabela payments criada."
)


# ============================================================
# 5. CRIAR ÍNDICES
# ============================================================

print(
    "\n4. Criando índices..."
)


cursor = conexao.cursor()


indices = [
    """
    CREATE INDEX IF NOT EXISTS
    idx_orders_order_id
    ON orders(order_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_orders_customer
    ON orders(customer_unique_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_orders_state
    ON orders(customer_state)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_items_order_id
    ON order_items(order_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_items_product
    ON order_items(product_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_items_category
    ON order_items(product_category)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_items_seller
    ON order_items(seller_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_payments_order
    ON payments(order_id)
    """,

    """
    CREATE INDEX IF NOT EXISTS
    idx_payments_type
    ON payments(payment_type)
    """,
]


for comando in indices:

    cursor.execute(comando)


conexao.commit()


print(
    "Índices criados."
)


# ============================================================
# 6. VALIDAR TABELAS
# ============================================================

print(
    "\n5. Validando banco..."
)


tabelas = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
    """,
    conexao
)


print(
    "\nTabelas encontradas:"
)

print(
    tabelas.to_string(
        index=False
    )
)


for tabela in [
    "orders",
    "order_items",
    "payments"
]:

    resultado = pd.read_sql_query(
        f"""
        SELECT COUNT(*) AS quantidade
        FROM {tabela}
        """,
        conexao
    )

    quantidade = int(
        resultado.iloc[0]["quantidade"]
    )

    print(
        f"{tabela}: {quantidade} registros"
    )


# ============================================================
# FINAL
# ============================================================

conexao.close()


print("\n========================================")
print("BANCO CRIADO COM SUCESSO")
print("========================================\n")


print(
    "Arquivo:"
)

print(
    ARQUIVO_BANCO
)