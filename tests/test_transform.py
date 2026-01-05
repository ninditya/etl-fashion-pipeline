import pandas as pd
from utils import transform

def test_transform_data_success():

    df_input = pd.DataFrame({
        "title": ["Product A", "Unknown Product", None],
        "price": ["$10", "$20", "$30"],
        "rating": ["4.5⭐", None, "3.0"],
        "colors": ["3", "2", None],
        "size": ["Size: M", "Size: L", "Size: S"],
        "gender": ["Gender: Male", "Gender: Female", None],
        "timestamp": ["2025-12-19T00:00:00"] * 3,
    })

    df_clean = transform.transform_data(df_input)

    assert not df_clean.empty

    assert all(df_clean["title"].str.lower() != "unknown product")

    assert df_clean["price"].dtype == float
    assert df_clean["rating"].dtype == float
    assert df_clean["colors"].dtype == int

    assert all("Size:" not in s for s in df_clean["size"])
    assert all("Gender:" not in g for g in df_clean["gender"])

def test_transform_data_empty():
    df_empty = pd.DataFrame()
    df_result = transform.transform_data(df_empty)

    assert df_result.empty

def test_transform_data_all_invalid():
    """
    DataFrame berisi semua invalid → harus dikembalikan kosong
    """
    df_invalid = pd.DataFrame({
        "title": ["Unknown Product", None],
        "price": [None, None],
        "rating": [None, None],
        "colors": [None, None],
        "size": ["Size: M", "Size: L"],
        "gender": ["Gender: Male", "Gender: Female"],
        "timestamp": ["2025-12-19T00:00:00"] * 2,
    })

    df_result = transform.transform_data(df_invalid)
    assert df_result.empty