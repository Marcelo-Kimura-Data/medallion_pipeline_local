from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).parents[3] / "data" / "raw"
BRONZE_DIR = Path(__file__).parents[3] / "data" / "bronze"


def extract(file_path: Path) -> pd.DataFrame:
    return pd.read_excel(file_path, dtype_backend="pyarrow")


def _add_metadata(df: pd.DataFrame, file_path: Path) -> pd.DataFrame:
    df["data_ingestao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    df["origem"] = file_path.name
    return df


def load(df: pd.DataFrame, file_path: Path) -> None:
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    df = _add_metadata(df, file_path)
    output_path = BRONZE_DIR / f"{file_path.stem}.parquet"
    df.to_parquet(output_path, index=False)


def run() -> None:
    for file in RAW_DIR.glob("*.xlsx"):
        df = extract(file)
        load(df, file)
        print(f"OK: {file.name} -> bronze/{file.stem}.parquet")


if __name__ == "__main__":
    run()
