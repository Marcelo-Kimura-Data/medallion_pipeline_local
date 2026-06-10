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
├── jupyter/
│   ├── read_bronze.ipynb
│   ├── read_silver.ipynb
│   └── read_gold.ipynb
├── src/local_medallion_pipeline/
│   ├── main.py
│   └── layers/
│       ├── bronze.py
│       ├── silver.py
│       └── gold.py
├── tests/
│   ├── test_bronze.py
│   ├── test_silver.py
│   └── test_gold.py
└── pyproject.toml
```

## Como rodar

Instalar dependências:
```bash
poetry install
```

Executar o pipeline completo:
```bash
poetry run python src/local_medallion_pipeline/main.py
poetry run run-pipeline
```

Ou executar cada etapa individualmente:
```bash
poetry run python src/local_medallion_pipeline/extract/bronze.py
poetry run python src/local_medallion_pipeline/extract/silver.py
poetry run python src/local_medallion_pipeline/extract/gold.py
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
| Bronze → Silver | Concluido |
| Silver → Gold | Concluido |
