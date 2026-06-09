import pandas as pd
import pytest

from local_medallion_pipeline.layers.gold import (
    transform_devolucoes_por_motivo,
    transform_fato_vendas,
    transform_vendas_por_loja,
    transform_vendas_por_periodo,
)


@pytest.fixture
def df_vendas() -> pd.DataFrame:
    return pd.DataFrame({
        "Data da Venda": pd.to_datetime(["2020-01-01", "2020-01-15", "2021-03-10"]),
        "Ordem de Compra": ["SO001", "SO002", "SO003"],
        "SKU": ["HL01", "HL02", "HL01"],
        "ID Cliente": [1001, 1002, 1001],
        "Qtd Vendida": [2, 1, 3],
        "ID Loja": [101, 102, 101],
        "data_ingestao": ["2026-01-01"] * 3,
        "origem": ["bronze/vendas"] * 3,
    })


@pytest.fixture
def df_produtos() -> pd.DataFrame:
    return pd.DataFrame({
        "SKU": ["HL01", "HL02"],
        "Produto": ["Produto A", "Produto B"],
        "Marca": ["Marca X", "Marca Y"],
        "Tipo do Produto": ["Tipo 1", "Tipo 2"],
        "Preço Unitario": [100.0, 50.0],
        "Custo Unitario": [40.0, 20.0],
    })


@pytest.fixture
def df_fato(df_vendas: pd.DataFrame, df_produtos: pd.DataFrame) -> pd.DataFrame:
    return transform_fato_vendas(df_vendas, df_produtos)


@pytest.fixture
def df_lojas() -> pd.DataFrame:
    return pd.DataFrame({
        "ID Loja": [101, 102],
        "Nome da Loja": ["Loja A", "Loja B"],
        "Tipo": ["Fisica", "Online"],
        "ID Localidade": [1, 2],
        "data_ingestao": ["2026-01-01"] * 2,
        "origem": ["silver/lojas"] * 2,
    })


@pytest.fixture
def df_localidades() -> pd.DataFrame:
    return pd.DataFrame({
        "ID Localidade": [1, 2],
        "País": ["Brasil", "EUA"],
        "Continente": ["América do Sul", "América do Norte"],
        "data_ingestao": ["2026-01-01"] * 2,
        "origem": ["silver/localidades"] * 2,
    })


@pytest.fixture
def df_devolucoes() -> pd.DataFrame:
    return pd.DataFrame({
        "Data Devolução": pd.to_datetime(["2020-02-01", "2020-03-05"]),
        "ID Loja": [101, 102],
        "SKU": ["HL01", "HL02"],
        "Qtd Devolvida": [1, 2],
        "Motivo Devolução": ["Produto com defeito", "Produto com defeito"],
        "data_ingestao": ["2026-01-01"] * 2,
        "origem": ["silver/devolucoes"] * 2,
    })


@pytest.fixture
def df_produtos_silver() -> pd.DataFrame:
    return pd.DataFrame({
        "SKU": ["HL01", "HL02"],
        "Produto": ["Produto A", "Produto B"],
        "Marca": ["Marca X", "Marca Y"],
        "Tipo do Produto": ["Tipo 1", "Tipo 2"],
        "Preço Unitario": [100.0, 50.0],
        "Custo Unitario": [40.0, 20.0],
        "data_ingestao": ["2026-01-01"] * 2,
        "origem": ["silver/produtos"] * 2,
    })


def test_transform_fato_vendas_colunas_calculadas(df_fato: pd.DataFrame) -> None:
    assert "valor_total" in df_fato.columns
    assert "custo_total" in df_fato.columns
    assert "lucro" in df_fato.columns


def test_transform_fato_vendas_calculo_correto(df_fato: pd.DataFrame) -> None:
    linha = df_fato[df_fato["SKU"] == "HL01"].iloc[0]
    assert linha["valor_total"] == linha["Qtd Vendida"] * linha["Preço Unitario"]
    assert linha["lucro"] == linha["valor_total"] - linha["custo_total"]


def test_transform_fato_vendas_join_produtos(df_fato: pd.DataFrame) -> None:
    assert "Produto" in df_fato.columns
    assert "Marca" in df_fato.columns
    assert df_fato["Produto"].notna().all()


def test_transform_vendas_por_periodo_agrupa_ano_mes(df_fato: pd.DataFrame) -> None:
    resultado = transform_vendas_por_periodo(df_fato)
    assert "ano" in resultado.columns
    assert "mes" in resultado.columns
    assert len(resultado) == 2


def test_transform_vendas_por_periodo_colunas_agg(df_fato: pd.DataFrame) -> None:
    resultado = transform_vendas_por_periodo(df_fato)
    for col in ["qtd_vendida", "valor_total", "custo_total", "lucro", "num_pedidos"]:
        assert col in resultado.columns


def test_transform_vendas_por_loja_join(
    df_fato: pd.DataFrame, df_lojas: pd.DataFrame, df_localidades: pd.DataFrame
) -> None:
    resultado = transform_vendas_por_loja(df_fato, df_lojas, df_localidades)
    assert "País" in resultado.columns
    assert "Continente" in resultado.columns
    assert "Nome da Loja" in resultado.columns


def test_transform_vendas_por_loja_agrupa_por_loja(
    df_fato: pd.DataFrame, df_lojas: pd.DataFrame, df_localidades: pd.DataFrame
) -> None:
    resultado = transform_vendas_por_loja(df_fato, df_lojas, df_localidades)
    assert len(resultado) == 2


def test_transform_devolucoes_por_motivo_agrupa(
    df_devolucoes: pd.DataFrame, df_produtos_silver: pd.DataFrame
) -> None:
    resultado = transform_devolucoes_por_motivo(df_devolucoes, df_produtos_silver)
    assert "Motivo Devolução" in resultado.columns
    assert "qtd_devolvida" in resultado.columns
    assert "num_ocorrencias" in resultado.columns


def test_transform_devolucoes_por_motivo_join_produtos(
    df_devolucoes: pd.DataFrame, df_produtos_silver: pd.DataFrame
) -> None:
    resultado = transform_devolucoes_por_motivo(df_devolucoes, df_produtos_silver)
    assert "Tipo do Produto" in resultado.columns
    assert "Marca" in resultado.columns
