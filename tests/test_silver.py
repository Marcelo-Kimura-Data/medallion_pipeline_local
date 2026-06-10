from pathlib import Path

import pandas as pd
import pytest

from local_medallion_pipeline.layers.silver import (
    transform_clientes,
    transform_devolucoes,
    transform_lojas,
    transform_produtos,
    transform_vendas,
)


@pytest.fixture
def df_vendas() -> pd.DataFrame:
    return pd.DataFrame({
        "Data da Venda": pd.to_datetime(["2020-01-01", "2021-06-15"]),
        "Ordem de Compra": ["SO001", "SO002"],
        "SKU": ["HL01", "HL02"],
        "ID Cliente": [1001, 1002],
        "Qtd Vendida": [2, 3],
        "ID Loja": [101, 102],
        "data_ingestao": ["2026-01-01 00:00:00", "2026-01-01 00:00:00"],
        "origem": ["bronze/Base Vendas - 2020.parquet", "bronze/Base Vendas - 2021.parquet"],
    })


@pytest.fixture
def df_clientes() -> pd.DataFrame:
    colunas = ["ID Cliente", "Primeiro Nome", "Sobrenome", "Email", "Genero",
               "Data Nascimento", "Estado Civil", "Num Filhos", "Nivel Escolar", "Documento"]
    linha_vazia = [None] * 10
    linha_header = colunas
    linha_dado1 = [11000, "JOAO", "SILVA", "joao@email.com", "M", "1/8/1990", "C", 2, "Superior Completo", "12345678900"]
    linha_dado2 = [11001, "MARIA", "SOUZA", "maria@email.com", "F", "5/3/1985", "S", 0, "Medio Completo", "98765432100"]
    rows = [linha_vazia, linha_header, linha_dado1, linha_dado2]
    df = pd.DataFrame(rows, columns=[f"Unnamed: {i}" for i in range(10)])
    df["data_ingestao"] = "2026-01-01 00:00:00"
    df["origem"] = "Cadastro Clientes.xlsx"
    return df


@pytest.fixture
def df_produtos() -> pd.DataFrame:
    return pd.DataFrame({
        "SKU": ["HL01", "HL02"],
        "Produto": ["Produto A", "Produto B"],
        "Marca": ["Marca X", "Marca Y"],
        "Tipo do Produto": ["Tipo 1", "Tipo 2"],
        "Preço Unitario": [99.9, 49.9],
        "Custo Unitario": [40.0, 20.0],
        "Observação": [None, None],
        "data_ingestao": ["2026-01-01 00:00:00", "2026-01-01 00:00:00"],
        "origem": ["Cadastro Produtos.xlsx", "Cadastro Produtos.xlsx"],
    })


@pytest.fixture
def df_lojas() -> pd.DataFrame:
    return pd.DataFrame({
        "ID Loja": [101, 102],
        "Nome da Loja": ["Loja A", "Loja B"],
        "Quantidade Colaboradores": [10, 20],
        "Tipo": ["Fisica", "Online"],
        "id Localidade": [1, 2],
        "Gerente Loja": ["Gerente A", "Gerente B"],
        "Documento Gerente": [12345678900, 98765432100],
        "data_ingestao": ["2026-01-01 00:00:00", "2026-01-01 00:00:00"],
        "origem": ["Cadastro Lojas.xlsx", "Cadastro Lojas.xlsx"],
    })


@pytest.fixture
def df_devolucoes() -> pd.DataFrame:
    return pd.DataFrame({
        "Data Devolução": pd.to_datetime(["2020-02-01", "2021-07-10"]),
        "ID Loja": [101, 102],
        "SKU": ["HL01", "HL02"],
        "Qtd Devolvida": [1, 2],
        "Motivo Devolução": ["Produto com defeito", "Arrependimento"],
        "data_ingestao": ["2026-01-01 00:00:00", "2026-01-01 00:00:00"],
        "origem": ["Base Devoluções.xlsx", "Base Devoluções.xlsx"],
    })


def test_transform_vendas_remove_metadados_bronze(df_vendas: pd.DataFrame) -> None:
    resultado = transform_vendas(df_vendas)
    assert "data_ingestao" in resultado.columns
    assert "origem" in resultado.columns
    assert resultado["origem"].iloc[0] == "bronze/Base Vendas - 2020|2021|2022.parquet"


def test_transform_vendas_mantem_colunas(df_vendas: pd.DataFrame) -> None:
    resultado = transform_vendas(df_vendas)
    for col in ["Data da Venda", "Ordem de Compra", "SKU", "ID Cliente", "Qtd Vendida", "ID Loja"]:
        assert col in resultado.columns


def test_transform_clientes_corrige_header(df_clientes: pd.DataFrame) -> None:
    resultado = transform_clientes(df_clientes)
    assert "ID Cliente" in resultado.columns
    assert "Primeiro Nome" in resultado.columns
    assert "Documento" in resultado.columns


def test_transform_clientes_remove_linhas_lixo(df_clientes: pd.DataFrame) -> None:
    resultado = transform_clientes(df_clientes)
    assert len(resultado) == 2


def test_transform_clientes_data_nascimento_datetime(df_clientes: pd.DataFrame) -> None:
    resultado = transform_clientes(df_clientes)
    assert pd.api.types.is_datetime64_any_dtype(resultado["Data Nascimento"])


def test_transform_produtos_remove_observacao(df_produtos: pd.DataFrame) -> None:
    resultado = transform_produtos(df_produtos)
    assert "Observação" not in resultado.columns


def test_transform_produtos_mantem_colunas(df_produtos: pd.DataFrame) -> None:
    resultado = transform_produtos(df_produtos)
    for col in ["SKU", "Produto", "Marca", "Tipo do Produto", "Preço Unitario", "Custo Unitario"]:
        assert col in resultado.columns


def test_transform_lojas_renomeia_id_localidade(df_lojas: pd.DataFrame) -> None:
    resultado = transform_lojas(df_lojas)
    assert "ID Localidade" in resultado.columns
    assert "id Localidade" not in resultado.columns


def test_transform_lojas_documento_gerente_string(df_lojas: pd.DataFrame) -> None:
    resultado = transform_lojas(df_lojas)
    assert pd.api.types.is_string_dtype(resultado["Documento Gerente"])


def test_transform_devolucoes_mantem_colunas(df_devolucoes: pd.DataFrame) -> None:
    resultado = transform_devolucoes(df_devolucoes)
    for col in ["Data Devolução", "ID Loja", "SKU", "Qtd Devolvida", "Motivo Devolução"]:
        assert col in resultado.columns


def test_transform_devolucoes_atualiza_origem(df_devolucoes: pd.DataFrame) -> None:
    resultado = transform_devolucoes(df_devolucoes)
    assert resultado["origem"].iloc[0] == "bronze/Base Devoluções.parquet"
