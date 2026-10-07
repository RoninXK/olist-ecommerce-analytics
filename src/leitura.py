from pathlib import Path
import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_RAW = PASTA_PROJETO / "data" / "raw"


arquivos = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


print("\n========================================")
print("OLIST ANALYTICS - LEITURA DOS DADOS")
print("========================================\n")


for nome_arquivo in arquivos:

    caminho = PASTA_RAW / nome_arquivo

    print(f"\nArquivo: {nome_arquivo}")

    if not caminho.exists():
        print("ERRO: arquivo não encontrado!")
        print(caminho)
        continue

    df = pd.read_csv(caminho)

    print(f"Linhas: {len(df)}")
    print(f"Colunas: {len(df.columns)}")

    print("\nColunas encontradas:")

    for coluna in df.columns:
        print(f" - {coluna}")

    print("\nPrimeiras linhas:")

    print(df.head(3))

    print("\n" + "=" * 50)