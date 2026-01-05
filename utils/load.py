import os
import pandas as pd
from sqlalchemy import create_engine
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import Optional

# KONFIGURASI CSV
CSV_OUTPUT_PATH = "products.csv"

# KONFIGURASI POSTGRESQL
DB_USERNAME = os.getenv("DB_USERNAME", "admin_fashion")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "database_fashion")
DB_TABLE_NAME = "products"

DATABASE_URL = (
    f"postgresql://{DB_USERNAME}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# KONFIGURASI GOOGLE SHEETS
GSHEET_SERVICE_ACCOUNT_FILE = "google-sheets-api.json"
GSHEET_ID = "1nKOSdLbGnllou1yGTFGQAtgbFPhXWZ2cVsDv13R668U"
GSHEET_RANGE = "Sheet1!A1"


def save_csv(df: pd.DataFrame):
    """Simpan DataFrame ke file CSV"""
    try:
        if df.empty:
            print("[CSV] Data kosong, tidak disimpan.")
            return

        df.to_csv(CSV_OUTPUT_PATH, index=False)
        print("[CSV] Berhasil disimpan.")

    except Exception as e:
        print(f"[CSV] Gagal: {e}")


def save_postgres(df: pd.DataFrame):
    """Simpan DataFrame ke PostgreSQL"""
    engine = None
    try:
        if df.empty:
            print("[PostgreSQL] Data kosong, tidak disimpan.")
            return

        engine = create_engine(DATABASE_URL)
        df.to_sql(DB_TABLE_NAME, con=engine, if_exists="replace", index=False)
        print("[PostgreSQL] Berhasil disimpan.")

    except Exception as e:
        print(f"[PostgreSQL] Gagal: {e}")

    finally:
        if engine:
            engine.dispose()


def save_gsheet(
    df: pd.DataFrame,
    service: Optional[object] = None,
    spreadsheet_id: str = GSHEET_ID,
    range_name: str = GSHEET_RANGE,
    credentials_file: str = GSHEET_SERVICE_ACCOUNT_FILE,
):
    """
    Simpan DataFrame ke Google Sheets.
    Service bisa di-mock untuk unit test.
    """
    try:
        if df.empty:
            print("[Google Sheets] Data kosong, tidak disimpan.")
            return

        if service is None:
            creds = Credentials.from_service_account_file(
                credentials_file,
                scopes=["https://www.googleapis.com/auth/spreadsheets"],
            )
            service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()
        values = [df.columns.tolist()] + df.values.tolist()

        # Bersihkan sheet
        sheet.values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name,
        ).execute()

        # Tulis data baru
        sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body={"values": values},
        ).execute()

        print("[Google Sheets] Berhasil disimpan.")

    except Exception as e:
        print(f"[Google Sheets] Gagal: {e}")
