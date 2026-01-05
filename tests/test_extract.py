# UNIT TEST | EXTRACT

import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock, patch
import requests
# Import module extract yang akan diuji
from utils import extract

# HELPER FUNCTIONS UNTUK MOCK HTML ELEMENT

def mock_p(text: str):
    p = MagicMock()
    p.text = text
    return p


def mock_card(
    title="Test Product",
    price="$100",
    rating="Rating: 5 ⭐",
    colors="3 Colors",
    size="Size: M",
    gender="Gender: Men",
):

    card = MagicMock()

    def find_side_effect(tag, class_name=None):
        if tag == "h3":
            return MagicMock(text=title)

        if tag == "span":
            return MagicMock(text=price)

        if tag == "div":
            detail = MagicMock()
            p_tags = []

            if rating:
                p_tags.append(mock_p(rating))
            if colors:
                p_tags.append(mock_p(colors))
            if size:
                p_tags.append(mock_p(size))
            if gender:
                p_tags.append(mock_p(gender))

            detail.find_all.return_value = p_tags
            return detail

        return None

    card.find.side_effect = find_side_effect
    return card

def test_extract_product_success_full_fields():

    card = mock_card()
    result = extract.extract_product(card)

    assert isinstance(result, dict)
    assert result["title"] == "Test Product"
    assert result["price"] == "$100"
    assert result["rating"] == "5"
    assert result["colors"] == "3"
    assert result["size"] == "M"
    assert result["gender"] == "Men"
    assert result["timestamp"] is not None


def test_extract_product_partial_missing_fields():

    card = mock_card(
        rating=None,
        colors=None,
        gender=None,
        size="Size: L",
    )

    result = extract.extract_product(card)

    assert result["title"] == "Test Product"
    assert result["price"] == "$100"
    assert result["rating"] is None
    assert result["colors"] is None
    assert result["size"] == "L"
    assert result["gender"] is None


def test_extract_product_exception_returns_none():

    card = MagicMock()
    card.find.side_effect = Exception("Broken HTML")

    result = extract.extract_product(card)
    assert result is None

@patch("utils.extract.requests.get")
def test_extract_data_success_mixed_products(mock_get):

    html = """
    <html>
        <div class="collection-card"></div>
        <div class="collection-card"></div>
    </html>
    """

    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    with patch("utils.extract.extract_product") as mock_extract:
        mock_extract.side_effect = [
            {
                "title": "A",
                "price": "$100",
                "rating": "5",
                "colors": "3",
                "size": "M",
                "gender": "Men",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "title": "B",
                "price": "$50",
                "rating": None,
                "colors": None,
                "size": "L",
                "gender": None,
                "timestamp": datetime.now().isoformat(),
            },
        ]

        df = extract.extract_data(max_page=1)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2


@patch("utils.extract.requests.get")
def test_extract_data_empty_page(mock_get):

    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    df = extract.extract_data(max_page=1)
    assert df.empty


@patch("utils.extract.requests.get", side_effect=Exception("Request failed"))
def test_extract_data_request_exception(mock_get):

    df = extract.extract_data(max_page=1)
    assert df.empty
