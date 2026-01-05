import pandas as pd
from unittest.mock import patch, MagicMock
from utils import load

df_dummy = pd.DataFrame({
    "title": ["A", "B"],
    "price": [160000, 320000],
    "rating": [4.5, 4.0],
    "colors": [3, 2],
    "size": ["M", "L"],
    "gender": ["Men", "Women"],
    "timestamp": ["2025-12-19T00:00:00"] * 2,
})

df_empty = pd.DataFrame()

def test_save_csv():

    with patch.object(pd.DataFrame, "to_csv") as mock_to_csv:
        load.save_csv(df_dummy)
        mock_to_csv.assert_called_once()

def test_save_csv_empty():

    with patch.object(pd.DataFrame, "to_csv") as mock_to_csv:
        load.save_csv(df_empty)
        mock_to_csv.assert_not_called()

def test_save_postgres():

    mock_engine = MagicMock()

    with patch("utils.load.create_engine", return_value=mock_engine), \
         patch.object(pd.DataFrame, "to_sql") as mock_to_sql:

        load.save_postgres(df_dummy)

        mock_to_sql.assert_called_once_with(
            load.DB_TABLE_NAME,
            con=mock_engine,
            if_exists="replace",
            index=False,
        )

def test_save_postgres_empty():
    with patch("builtins.print") as mock_print:
        load.save_postgres(df_empty)
        mock_print.assert_called_with("[PostgreSQL] Data kosong, tidak disimpan.")

def test_save_postgres_exception():
    with patch("utils.load.create_engine", side_effect=Exception("DB error")), \
         patch("builtins.print") as mock_print:
        load.save_postgres(df_dummy)
        mock_print.assert_called()

def test_save_gsheet():

    mock_service = MagicMock()
    mock_values = MagicMock()

    mock_service.spreadsheets.return_value.values.return_value = mock_values
    mock_values.clear.return_value.execute.return_value = None
    mock_values.update.return_value.execute.return_value = None

    load.save_gsheet(df_dummy, service=mock_service)

    mock_values.clear.assert_called_once()
    mock_values.update.assert_called_once()

def test_save_gsheet_empty():
    with patch("builtins.print") as mock_print:
        load.save_gsheet(df_empty, service=MagicMock())
        mock_print.assert_called_with("[Google Sheets] Data kosong, tidak disimpan.")