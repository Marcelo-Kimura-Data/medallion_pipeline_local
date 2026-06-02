from pathlib import Path

import pandas as pd
import pytest

from local_medallion_pipeline.extract.raw_to_bronze import extract, load


@pytest.fixture
def sample_excel(tmp_path: Path) -> Path:
    file = tmp_path / "vendas.xlsx"
    df = pd.DataFrame({"produto": ["A", "B"], "valor": [10.0, 20.0]})
    df.to_excel(file, index=False)
    return file


def test_extract_retorna_dataframe(sample_excel: Path) -> None:
    df = extract(sample_excel)
    assert isinstance(df, pd.DataFrame)


def test_extract_colunas_corretas(sample_excel: Path) -> None:
    df = extract(sample_excel)
    assert list(df.columns) == ["produto", "valor"]


def test_extract_quantidade_linhas(sample_excel: Path) -> None:
    df = extract(sample_excel)
    assert len(df) == 2


def test_load_cria_arquivo_parquet(tmp_path: Path, sample_excel: Path) -> None:
    df = extract(sample_excel)

    # Sobrescreve BRONZE_DIR temporariamente para o teste
    import local_medallion_pipeline.extract.raw_to_bronze as module

    original = module.BRONZE_DIR
    module.BRONZE_DIR = tmp_path
    try:
        load(df, sample_excel)
    finally:
        module.BRONZE_DIR = original

    parquet_file = tmp_path / "vendas.parquet"
    assert parquet_file.exists()


def test_load_parquet_conteudo_correto(tmp_path: Path, sample_excel: Path) -> None:
    df = extract(sample_excel)

    import local_medallion_pipeline.extract.raw_to_bronze as module

    original = module.BRONZE_DIR
    module.BRONZE_DIR = tmp_path
    try:
        load(df, sample_excel)
    finally:
        module.BRONZE_DIR = original

    resultado = pd.read_parquet(tmp_path / "vendas.parquet")
    assert list(resultado.columns) == ["produto", "valor"]
    assert len(resultado) == 2
