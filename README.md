# Local Medallion Pipeline

Pipeline de dados local seguindo a arquitetura medallion (Raw → Bronze → Silver → Gold).

## Sobre o projeto

Projeto de estudo para praticar boas práticas de engenharia de dados com Python, processando dados de vendas de varejo no formato Excel e transformando-os em Parquet ao longo das camadas da arquitetura medallion.

## Tecnologias

- Python 3.13
- pandas + pyarrow
- openpyxl
- pytest
- ruff
- Poetry

## Estrutura

```
local-medallion-pipeline/
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── src/local_medallion_pipeline/
│   └── extract/
│       ├── bronze.py
│       ├── silver.py
│       └── gold.py
├── tests/
│   └── test_raw_to_bronze.py
└── pyproject.toml
```

## Como rodar

Instalar dependências:
```bash
poetry install
```

Executar a etapa Raw → Bronze:
```bash
poetry run python src/local_medallion_pipeline/extract/bronze.py
```

Rodar os testes:
```bash
poetry run pytest
```

Lint e formatação:
```bash
poetry run task lint
poetry run task format
```

## Status

| Etapa | Status |
|---|---|
| Raw → Bronze | Concluido |
| Bronze → Silver | Em desenvolvimento |
| Silver → Gold | Em desenvolvimento |
