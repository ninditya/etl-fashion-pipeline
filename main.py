from utils import extract, transform, load


def main():
    print("\n===== MEMULAI PIPELINE ETL PRODUK FASHION =====\n")

    # EXTRACT
    raw_data = extract.extract_data()
    if raw_data.empty:
        print("[ERROR] Tidak ada data hasil extract. Pipeline dihentikan.\n")
        return

    # TRANSFORM
    clean_data = transform.transform_data(raw_data)
    if clean_data.empty:
        print("[ERROR] Semua data invalid. Pipeline dihentikan.\n")
        return

    # LOAD
    print(">>> MEMULAI LOAD DATA KE REPOSITORI")
    load.save_csv(clean_data)
    load.save_postgres(clean_data)
    load.save_gsheet(clean_data)
    print("\n===== PIPELINE SELESAI =====")


if __name__ == "__main__":
    main()
