from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SILVER_DIR = Path(__file__).parents[3] / "data" / "silver"
GOLD_DIR = Path(__file__).parents[3] / "data" / "gold"


def extract_fato_vendas() -> tuple[pd.DataFrame, pd.DataFrame]:
    vendas = pd.read_parquet(SILVER_DIR / "vendas.parquet")
    produtos = pd.read_parquet(SILVER_DIR / "produtos.parquet")
    return vendas, produtos


def transform_fato_vendas(vendas: pd.DataFrame, produtos: pd.DataFrame) -> pd.DataFrame:
    df = vendas.merge(
        produtos[["SKU", "Produto", "Marca", "Tipo do Produto", "Preço Unitario", "Custo Unitario"]],
        on="SKU",
        how="left",
    )

    df["valor_total"] = df["Qtd Vendida"] * df["Preço Unitario"]
    df["custo_total"] = df["Qtd Vendida"] * df["Custo Unitario"]
    df["lucro"] = df["valor_total"] - df["custo_total"]

    df = df.drop(columns=["data_ingestao", "origem"])
    df["data_ingestao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    df["origem"] = "silver/vendas.parquet + silver/produtos.parquet"
    return df


def load_fato_vendas(df: pd.DataFrame) -> None:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GOLD_DIR / "fato_vendas.parquet"
    df.to_parquet(output_path, index=False)
    print(f"OK: fato_vendas -> gold/fato_vendas.parquet ({len(df)} linhas)")


def extract_vendas_por_periodo() -> pd.DataFrame:
    return pd.read_parquet(GOLD_DIR / "fato_vendas.parquet")


def transform_vendas_por_periodo(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ano"] = df["Data da Venda"].dt.year
    df["mes"] = df["Data da Venda"].dt.month

    agg = (
        df.groupby(["ano", "mes"], as_index=False)
        .agg(
            qtd_vendida=("Qtd Vendida", "sum"),
            valor_total=("valor_total", "sum"),
            custo_total=("custo_total", "sum"),
            lucro=("lucro", "sum"),
            num_pedidos=("Ordem de Compra", "nunique"),
        )
        .sort_values(["ano", "mes"])
        .reset_index(drop=True)
    )

    agg["data_ingestao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    agg["origem"] = "gold/fato_vendas.parquet"
    return agg


def load_vendas_por_periodo(df: pd.DataFrame) -> None:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GOLD_DIR / "vendas_por_periodo.parquet"
    df.to_parquet(output_path, index=False)
    print(f"OK: vendas_por_periodo -> gold/vendas_por_periodo.parquet ({len(df)} linhas)")


def extract_vendas_por_loja() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    fato = pd.read_parquet(GOLD_DIR / "fato_vendas.parquet")
    lojas = pd.read_parquet(SILVER_DIR / "lojas.parquet")
    localidades = pd.read_parquet(SILVER_DIR / "localidades.parquet")
    return fato, lojas, localidades


def transform_vendas_por_loja(
    fato: pd.DataFrame, lojas: pd.DataFrame, localidades: pd.DataFrame
) -> pd.DataFrame:
    lojas_local = lojas.merge(
        localidades[["ID Localidade", "País", "Continente"]],
        on="ID Localidade",
        how="left",
    )

    df = fato.merge(
        lojas_local[["ID Loja", "Nome da Loja", "Tipo", "País", "Continente"]],
        on="ID Loja",
        how="left",
    )

    agg = (
        df.groupby(["ID Loja", "Nome da Loja", "Tipo", "País", "Continente"], as_index=False)
        .agg(
            qtd_vendida=("Qtd Vendida", "sum"),
            valor_total=("valor_total", "sum"),
            custo_total=("custo_total", "sum"),
            lucro=("lucro", "sum"),
            num_pedidos=("Ordem de Compra", "nunique"),
        )
        .sort_values("valor_total", ascending=False)
        .reset_index(drop=True)
    )

    agg["data_ingestao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    agg["origem"] = "gold/fato_vendas.parquet + silver/lojas.parquet + silver/localidades.parquet"
    return agg


def load_vendas_por_loja(df: pd.DataFrame) -> None:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GOLD_DIR / "vendas_por_loja.parquet"
    df.to_parquet(output_path, index=False)
    print(f"OK: vendas_por_loja -> gold/vendas_por_loja.parquet ({len(df)} linhas)")


def extract_devolucoes_por_motivo() -> tuple[pd.DataFrame, pd.DataFrame]:
    devolucoes = pd.read_parquet(SILVER_DIR / "devolucoes.parquet")
    produtos = pd.read_parquet(SILVER_DIR / "produtos.parquet")
    return devolucoes, produtos


def transform_devolucoes_por_motivo(
    devolucoes: pd.DataFrame, produtos: pd.DataFrame
) -> pd.DataFrame:
    df = devolucoes.merge(
        produtos[["SKU", "Produto", "Marca", "Tipo do Produto"]],
        on="SKU",
        how="left",
    )

    agg = (
        df.groupby(["Motivo Devolução", "Tipo do Produto", "Marca"], as_index=False)
        .agg(
            qtd_devolvida=("Qtd Devolvida", "sum"),
            num_ocorrencias=("SKU", "count"),
        )
        .sort_values("qtd_devolvida", ascending=False)
        .reset_index(drop=True)
    )

    agg["data_ingestao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    agg["origem"] = "silver/devolucoes.parquet + silver/produtos.parquet"
    return agg


def load_devolucoes_por_motivo(df: pd.DataFrame) -> None:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GOLD_DIR / "devolucoes_por_motivo.parquet"
    df.to_parquet(output_path, index=False)
    print(f"OK: devolucoes_por_motivo -> gold/devolucoes_por_motivo.parquet ({len(df)} linhas)")


def run() -> None:
    vendas, produtos = extract_fato_vendas()
    df_fato = transform_fato_vendas(vendas, produtos)
    load_fato_vendas(df_fato)

    df_periodo = extract_vendas_por_periodo()
    df_periodo = transform_vendas_por_periodo(df_periodo)
    load_vendas_por_periodo(df_periodo)

    fato, lojas, localidades = extract_vendas_por_loja()
    df_loja = transform_vendas_por_loja(fato, lojas, localidades)
    load_vendas_por_loja(df_loja)

    devolucoes, produtos = extract_devolucoes_por_motivo()
    df_dev = transform_devolucoes_por_motivo(devolucoes, produtos)
    load_devolucoes_por_motivo(df_dev)


if __name__ == "__main__":
    run()
