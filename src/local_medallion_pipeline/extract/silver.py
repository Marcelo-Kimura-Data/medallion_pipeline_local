from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

BRONZE_DIR = Path(__file__).parents[3] / "data" / "bronze"
SILVER_DIR = Path(__file__).parents[3] / "data" / "silver"


def extract_vendas() -> pd.DataFrame:
    arquivos = [
        "Base Vendas - 2020.parquet",
        "Base Vendas - 2021.parquet",
        "Base Vendas - 2022.parquet",
    ]
    dfs = [pd.read_parquet(BRONZE_DIR / f) for f in arquivos]
    return pd.concat(dfs, ignore_index=True)


def transform_vendas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["data_ingestao", "origem"])
    df["data_ingestao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    df["origem"] = "bronze/Base Vendas - 2020|2021|2022.parquet"
    return df


def load_vendas(df: pd.DataFrame) -> None:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SILVER_DIR / "vendas.parquet"
    df.to_parquet(output_path, index=False)
    print(f"OK: vendas consolidadas -> silver/vendas.parquet ({len(df)} linhas)")


def extract_clientes() -> pd.DataFrame:
    return pd.read_parquet(BRONZE_DIR / "Cadastro Clientes.parquet")


def transform_clientes(df: pd.DataFrame) -> pd.DataFrame:
    # linha 0 vazia e linha 1 com os nomes reais das colunas (problema no Excel original)
    colunas = df.iloc[1, :10].tolist()
    df = df.iloc[2:, :10].copy()
    df.columns = colunas
    df = df.reset_index(drop=True)

    df["Data Nascimento"] = pd.to_datetime(df["Data Nascimento"], dayfirst=False, errors="coerce")
    df["Documento"] = df["Documento"].astype(str)

    df["data_ingestao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    df["origem"] = "bronze/Cadastro Clientes.parquet"
    return df


def load_clientes(df: pd.DataFrame) -> None:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SILVER_DIR / "clientes.parquet"
    df.to_parquet(output_path, index=False)
    print(f"OK: clientes -> silver/clientes.parquet ({len(df)} linhas)")


def extract_produtos() -> pd.DataFrame:
    return pd.read_parquet(BRONZE_DIR / "Cadastro Produtos.parquet")


def transform_produtos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["Observação", "data_ingestao", "origem"])
    df["data_ingestao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    df["origem"] = "bronze/Cadastro Produtos.parquet"
    return df


def load_produtos(df: pd.DataFrame) -> None:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SILVER_DIR / "produtos.parquet"
    df.to_parquet(output_path, index=False)
    print(f"OK: produtos -> silver/produtos.parquet ({len(df)} linhas)")


def extract_lojas() -> pd.DataFrame:
    return pd.read_parquet(BRONZE_DIR / "Cadastro Lojas.parquet")


def transform_lojas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["data_ingestao", "origem"])
    df = df.rename(columns={"id Localidade": "ID Localidade"})
    df["Documento Gerente"] = df["Documento Gerente"].astype(str)
    df["data_ingestao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    df["origem"] = "bronze/Cadastro Lojas.parquet"
    return df


def load_lojas(df: pd.DataFrame) -> None:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SILVER_DIR / "lojas.parquet"
    df.to_parquet(output_path, index=False)
    print(f"OK: lojas -> silver/lojas.parquet ({len(df)} linhas)")


def extract_localidades() -> pd.DataFrame:
    return pd.read_parquet(BRONZE_DIR / "Cadastro Localidades.parquet")


def transform_localidades(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["data_ingestao", "origem"])
    df["data_ingestao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    df["origem"] = "bronze/Cadastro Localidades.parquet"
    return df


def load_localidades(df: pd.DataFrame) -> None:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SILVER_DIR / "localidades.parquet"
    df.to_parquet(output_path, index=False)
    print(f"OK: localidades -> silver/localidades.parquet ({len(df)} linhas)")


def extract_devolucoes() -> pd.DataFrame:
    return pd.read_parquet(BRONZE_DIR / "Base Devoluções.parquet")


def transform_devolucoes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["data_ingestao", "origem"])
    df["data_ingestao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    df["origem"] = "bronze/Base Devoluções.parquet"
    return df


def load_devolucoes(df: pd.DataFrame) -> None:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SILVER_DIR / "devolucoes.parquet"
    df.to_parquet(output_path, index=False)
    print(f"OK: devolucoes -> silver/devolucoes.parquet ({len(df)} linhas)")


def run() -> None:
    df_vendas = extract_vendas()
    df_vendas = transform_vendas(df_vendas)
    load_vendas(df_vendas)

    df_clientes = extract_clientes()
    df_clientes = transform_clientes(df_clientes)
    load_clientes(df_clientes)

    df_produtos = extract_produtos()
    df_produtos = transform_produtos(df_produtos)
    load_produtos(df_produtos)

    df_lojas = extract_lojas()
    df_lojas = transform_lojas(df_lojas)
    load_lojas(df_lojas)

    df_localidades = extract_localidades()
    df_localidades = transform_localidades(df_localidades)
    load_localidades(df_localidades)

    df_devolucoes = extract_devolucoes()
    df_devolucoes = transform_devolucoes(df_devolucoes)
    load_devolucoes(df_devolucoes)


if __name__ == "__main__":
    run()
