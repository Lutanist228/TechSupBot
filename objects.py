import csv

class DataParser():
    def __init__(self, path: str, format: str) -> None:
        self.path = path
        self.format = format
        
    def read_info(self):
        data = []
        with open(self.path, "r", encoding="utf-8") as file:
            match self.format:
                case "csv":
                    reader = csv.DictReader(file)
                    for row in reader:
                        data.append(row)
                    return data
        
        