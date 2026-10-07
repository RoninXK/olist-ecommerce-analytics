from pathlib import Path
import sqlite3
import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA_PROJETO = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

PASTA_SQL = (
    PASTA_PROJETO
    / "sql"
)

BANCO = (
    PASTA_PROJETO
    / "data"
    / "processed"
    / "olist_analytics.db"
)


# ============================================================
# CONEXÃO
# ============================================================

conexao = sqlite3.connect(
    BANCO
)


print("\n========================================")
print("OLIST ANALYTICS - CONSULTAS SQL")
print("========================================\n")


# ============================================================
# LOCALIZAR CONSULTAS
# ============================================================

arquivos_sql = sorted(
    PASTA_SQL.glob("*.sql")
)


if not arquivos_sql:

    print(
        "Nenhuma consulta SQL encontrada."
    )

    conexao.close()

    raise SystemExit


# ============================================================
# EXECUTAR CONSULTAS
# ============================================================

for arquivo in arquivos_sql:

    print("\n========================================")

    print(
        arquivo.name
    )

    print(
        "========================================\n"
    )


    consulta = (
        arquivo
        .read_text(
            encoding="utf-8"
        )
    )


    try:

        resultado = pd.read_sql_query(
            consulta,
            conexao
        )


        print(
            resultado
            .head(20)
            .to_string(
                index=False
            )
        )


        print(
            f"\nLinhas retornadas: "
            f"{len(resultado)}"
        )


    except Exception as erro:

        print(
            "ERRO AO EXECUTAR:"
        )

        print(
            erro
        )


# ============================================================
# FINAL
# ============================================================

conexao.close()


print("\n========================================")
print("CONSULTAS FINALIZADAS")
print("========================================")