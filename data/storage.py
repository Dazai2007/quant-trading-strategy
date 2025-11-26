import pandas as pd
import os

class DataStorage:
    def __init__(self, data_dir='data_storage'):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def save_to_parquet(self, df, filename):
        path = os.path.join(self.data_dir, filename)
        df.to_parquet(path)
        print(f"Saved to {path}")

    def load_from_parquet(self, filename):
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            return pd.read_parquet(path)
        else:
            print(f"File not found: {path}")
            return None
