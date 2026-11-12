from pathlib import Path
import csv

def load_rows(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

if __name__ == "__main__":
    for row in load_rows(Path(__file__).with_name("맛집.csv")):
        print(" | ".join(f"{k}: {v}" for k,v in row.items()))
