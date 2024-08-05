import csv
from config import *

def create_csv(file_path: str) -> csv.excel:
    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(
            categories
        )

