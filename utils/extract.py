import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from typing import Dict, Optional, List, Any

BASE_URL = "https://fashion-studio.dicoding.dev"
MAX_PAGE = 50
HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 15


def extract_product(card) -> Optional[Dict[str, Any]]:
    """Extract satu produk dari HTML card."""

    try:
        def safe_find(tag, class_name):
            try:
                return card.find(tag, class_=class_name)
            except TypeError:
                return card.find(tag, class_name)

        title_tag = safe_find("h3", "product-title")
        price_tag = safe_find("span", "price")
        detail_box = safe_find("div", "product-details")

        title = title_tag.text.strip() if title_tag else None
        price = price_tag.text.strip() if price_tag else None

        rating = colors = size = gender = None

        p_tags = detail_box.find_all("p") if detail_box else []

        if detail_box:
            for p in detail_box.find_all("p"):
                text = p.text.strip()

                if "Rating" in text:
                    rating = text.replace("Rating:", "").replace("⭐", "").strip()
                elif "Colors" in text:
                    colors = text.replace("Colors", "").replace(":", "").strip()
                elif "Size" in text:
                    size = text.replace("Size:", "").strip()
                elif "Gender" in text:
                    gender = text.replace("Gender:", "").strip()
        return {
            "title": title,
            "price": price,
            "rating": rating,
            "colors": colors,
            "size": size,
            "gender": gender,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception:
        return None


def extract_data(max_page: int = MAX_PAGE) -> pd.DataFrame:
    """Scrape data produk dari seluruh halaman."""

    results: List[Dict[str, Any]] = []

    print(">>> MEMULAI EXTRACT DATA | WEB SCRAPING FASHION STUDIO")

    for page in range(1, max_page + 1):
        url = BASE_URL if page == 1 else f"{BASE_URL}/page{page}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.find_all("div", class_="collection-card")

            for card in cards:
                product = extract_product(card)
                if product:
                    results.append(product)

            print(f"Halaman {page}: {len(cards)} produk ditemukan, total terkumpul {len(results)}")
        
        except requests.exceptions.RequestException as e:
            print(f"Gagal mengambil data dari {url}: {e}")
            continue
        
        except Exception as e:
            print(f"Halaman {page}: Gagal diakses ({e}), dilewati.")
            continue

    print(f"<<< EXTRACT SELESAI | Total produk berhasil di-scrap: {len(results)} >>>\n")
    return pd.DataFrame(results)
