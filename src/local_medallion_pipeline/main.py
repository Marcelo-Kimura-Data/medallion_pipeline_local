from local_medallion_pipeline.layers.bronze import run as run_bronze
from local_medallion_pipeline.layers.silver import run as run_silver
from local_medallion_pipeline.layers.gold import run as run_gold


def main() -> None:
    print("=== RAW -> BRONZE ===")
    run_bronze()

    print("\n=== BRONZE -> SILVER ===")
    run_silver()

    print("\n=== SILVER -> GOLD ===")
    run_gold()


if __name__ == "__main__":
    main()
