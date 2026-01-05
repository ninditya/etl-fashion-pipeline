import os
from numpy import int64
import pandas as pd


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """ Membersihkan dan mentransformasi data hasil extract: """

    print(">>> MEMULAI TRANSFORM DATA | CLEAN DATA FASHION STUDIO")

    try:
        if df.empty:
            print("Data kosong. Transform dibatalkan.")
            return df

        df = df.copy()
        total_awal = len(df)

        df = df[df["title"].notna()]
        df = df[df["title"].str.lower() != "unknown product"]
        df = df[df["price"].notna()]
        df = df[df["rating"].notna()]
        df = df[df["price"].str.contains(r"\d", regex=True)]

        total_invalid = total_awal - len(df)

        EXCHANGE_RATE = float(os.getenv("EXCHANGE_RATE_USD_TO_IDR", 16000))

        df["price"] = df["price"].str.replace(r"[$,]", "", regex=True)
        df["price"] = df["price"].astype(float) * EXCHANGE_RATE
        df["rating"] = df["rating"].str.extract(r"([\d.]+)")[0].astype(float)
        df["colors"] = df["colors"].str.extract(r"(\d+)")[0].astype(int64)
        df["size"] = df["size"].str.replace("Size:", "").str.strip()
        df["gender"] = df["gender"].str.replace("Gender:", "").str.strip()

        df.dropna(inplace=True)
        
        df = df.astype({
            'price': 'float64',
            'rating': 'float64',
            'colors': 'int64',
            'title': 'object',
            'size': 'object',
            'gender': 'object'
        })
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)

        print(f"Data invalid / dibuang: {total_invalid}\n")
        print(f"Data types:\n{df.dtypes}\n")
        print(f"Data :\n{df.head()}\n")
        print(f"<<< TRANSFORM SELESAI | Total data bersih: {len(df)} >>>\n")

        return df

    except Exception:
        print("Terjadi error saat transform data.")
        return pd.DataFrame()
