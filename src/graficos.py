from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_DADOS = PASTA_PROJETO / "data" / "processed"
PASTA_IMAGENS = PASTA_PROJETO / "images"

PASTA_IMAGENS.mkdir(
    parents=True,
    exist_ok=True
)


print("\n========================================")
print("OLIST ANALYTICS - GERAÇÃO DE GRÁFICOS")
print("========================================\n")


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def reais(valor, pos):
    if abs(valor) >= 1_000_000:
        return f"R$ {valor / 1_000_000:.1f}M"

    if abs(valor) >= 1_000:
        return f"R$ {valor / 1_000:.0f} mil"

    return f"R$ {valor:.0f}"


def salvar(nome):
    caminho = PASTA_IMAGENS / nome

    plt.tight_layout()

    plt.savefig(
        caminho,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Criado: {nome}")


# ============================================================
# CARREGAR DADOS
# ============================================================

print("Carregando dados...")


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


# Somente vendas concluídas
pedidos = pedidos[
    pedidos["order_status"] == "delivered"
].copy()


ids_entregues = set(
    pedidos["order_id"]
)


itens = itens[
    itens["order_id"].isin(ids_entregues)
].copy()


pagamentos = pagamentos[
    pagamentos["order_id"].isin(ids_entregues)
].copy()


# ============================================================
# 1. FATURAMENTO MENSAL
# ============================================================

pedidos["ano_mes"] = (
    pedidos["order_purchase_timestamp"]
    .dt.to_period("M")
    .astype(str)
)


faturamento_mes = (
    pedidos
    .groupby("ano_mes")["payment_total"]
    .sum()
)


plt.figure(figsize=(12, 6))

plt.plot(
    faturamento_mes.index,
    faturamento_mes.values,
    marker="o"
)

plt.title(
    "Evolução Mensal do Faturamento"
)

plt.xlabel(
    "Mês"
)

plt.ylabel(
    "Faturamento"
)

plt.xticks(
    rotation=45
)

plt.gca().yaxis.set_major_formatter(
    FuncFormatter(reais)
)

plt.grid(
    alpha=0.25
)

salvar(
    "faturamento_mensal.png"
)


# ============================================================
# 2. TOP 10 ESTADOS
# ============================================================

estados = (
    pedidos
    .groupby("customer_state")["payment_total"]
    .sum()
    .sort_values(
        ascending=False
    )
    .head(10)
    .sort_values()
)


plt.figure(figsize=(10, 6))

plt.barh(
    estados.index,
    estados.values
)

plt.title(
    "Top 10 Estados por Faturamento"
)

plt.xlabel(
    "Faturamento"
)

plt.ylabel(
    "Estado"
)

plt.gca().xaxis.set_major_formatter(
    FuncFormatter(reais)
)

salvar(
    "top10_estados_faturamento.png"
)


# ============================================================
# 3. TOP 10 CATEGORIAS
# ============================================================

categorias = (
    itens
    .groupby("product_category")["price"]
    .sum()
    .sort_values(
        ascending=False
    )
    .head(10)
    .sort_values()
)


categorias.index = [
    categoria
    .replace("_", " ")
    .title()

    for categoria
    in categorias.index
]


plt.figure(figsize=(11, 7))

plt.barh(
    categorias.index,
    categorias.values
)

plt.title(
    "Top 10 Categorias por Faturamento"
)

plt.xlabel(
    "Faturamento dos Produtos"
)

plt.ylabel(
    "Categoria"
)

plt.gca().xaxis.set_major_formatter(
    FuncFormatter(reais)
)

salvar(
    "top10_categorias.png"
)


# ============================================================
# 4. FORMAS DE PAGAMENTO
# ============================================================

formas_pagamento = (
    pagamentos
    .groupby("payment_type")["payment_value"]
    .sum()
    .sort_values(
        ascending=False
    )
)


plt.figure(figsize=(9, 6))

plt.bar(
    formas_pagamento.index,
    formas_pagamento.values
)

plt.title(
    "Valor por Forma de Pagamento"
)

plt.xlabel(
    "Forma de Pagamento"
)

plt.ylabel(
    "Valor"
)

plt.gca().yaxis.set_major_formatter(
    FuncFormatter(reais)
)

plt.xticks(
    rotation=20
)

salvar(
    "formas_pagamento.png"
)


# ============================================================
# 5. DISTRIBUIÇÃO DAS AVALIAÇÕES
# ============================================================

avaliacoes = (
    pedidos["review_score"]
    .dropna()
    .value_counts()
    .sort_index()
)


plt.figure(figsize=(8, 5))

plt.bar(
    avaliacoes.index.astype(int),
    avaliacoes.values
)

plt.title(
    "Distribuição das Avaliações dos Clientes"
)

plt.xlabel(
    "Nota"
)

plt.ylabel(
    "Quantidade de Avaliações"
)

plt.xticks(
    [1, 2, 3, 4, 5]
)

salvar(
    "distribuicao_avaliacoes.png"
)


# ============================================================
# 6. IMPACTO DO ATRASO NA AVALIAÇÃO
# ============================================================

avaliacao_entrega = pedidos[
    pedidos["review_score"].notna()
    &
    pedidos["delivery_difference_days"].notna()
].copy()


avaliacao_entrega["situacao"] = (
    avaliacao_entrega[
        "delivery_difference_days"
    ]
    .apply(
        lambda x:
        "Atrasado"
        if x > 0
        else "No prazo"
    )
)


nota_entrega = (
    avaliacao_entrega
    .groupby("situacao")["review_score"]
    .mean()
    .reindex(
        ["No prazo", "Atrasado"]
    )
)


plt.figure(figsize=(7, 5))

plt.bar(
    nota_entrega.index,
    nota_entrega.values
)

plt.title(
    "Impacto do Atraso na Avaliação"
)

plt.xlabel(
    "Situação da Entrega"
)

plt.ylabel(
    "Nota Média"
)

plt.ylim(
    0,
    5
)


for indice, valor in enumerate(
    nota_entrega.values
):

    plt.text(
        indice,
        valor + 0.08,
        f"{valor:.2f}",
        ha="center",
        fontsize=11
    )


salvar(
    "avaliacao_atraso.png"
)


# ============================================================
# 7. TEMPO MÉDIO DE ENTREGA POR ESTADO
# ============================================================

entregas_estado = (
    pedidos[
        pedidos["delivery_days"].notna()
    ]
    .groupby("customer_state")["delivery_days"]
    .mean()
    .sort_values(
        ascending=False
    )
    .head(10)
    .sort_values()
)


plt.figure(figsize=(10, 6))

plt.barh(
    entregas_estado.index,
    entregas_estado.values
)

plt.title(
    "Estados com Maior Tempo Médio de Entrega"
)

plt.xlabel(
    "Tempo Médio de Entrega (dias)"
)

plt.ylabel(
    "Estado"
)

salvar(
    "tempo_entrega_estados.png"
)


# ============================================================
# 8. STATUS DOS PEDIDOS
# ============================================================

todos_pedidos = pd.read_csv(
    PASTA_DADOS / "olist_orders_analytics.csv"
)


status = (
    todos_pedidos[
        "order_status"
    ]
    .value_counts()
    .sort_values()
)


plt.figure(figsize=(10, 6))

plt.barh(
    status.index,
    status.values
)

plt.title(
    "Distribuição dos Status dos Pedidos"
)

plt.xlabel(
    "Quantidade"
)

plt.ylabel(
    "Status"
)


salvar(
    "status_pedidos.png"
)


# ============================================================
# FINAL
# ============================================================

print("\n========================================")
print("GRÁFICOS GERADOS COM SUCESSO")
print("========================================\n")

print(
    f"Imagens salvas em:\n{PASTA_IMAGENS}"
)