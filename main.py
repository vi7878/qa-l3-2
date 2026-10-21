import pytest
import requests
BASE_URL = "https://api.novaposhta.ua/v2.0/json/"
API_KEY = ""
def test_1_basic_api_functions_get_areas():
    payload = {
        "apiKey": API_KEY,
        "modelName": "Address",
        "calledMethod": "getAreas",
        "methodProperties": {}
    }
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == 200
    assert "application/json" in response.headers.get("Content-Type", "")
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) > 20  # В Україні понад 20 областей
    assert "Description" in body["data"][0]
    assert "Ref" in body["data"][0]
def test_2_search_and_filter_settlements():
    payload = {
        "apiKey": API_KEY,
        "modelName": "Address",
        "calledMethod": "searchSettlements",
        "methodProperties": {
            "CityName": "Черкаси",
            "Limit": "5",
            "Page": "1"
        }
    }
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) > 0
    addresses = body["data"][0]["Addresses"]
    assert len(addresses) <= 5
    assert "Черкаси" in addresses[0]["MainDescription"]
def test_3_filter_warehouses_by_city():
    payload = {
        "apiKey": API_KEY,
        "modelName": "Address",
        "calledMethod": "getWarehouses",
        "methodProperties": {
            "CityName": "Черкаси",
            "WarehouseId": "1",
            "Limit": "10",
            "Page": "1"
        }
    }
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) > 0
    assert "Черкаси" in body["data"][0]["CityDescription"]
def test_4_validation_on_create_resource():
    payload = {
        "apiKey": API_KEY,
        "modelName": "Counterparty",
        "calledMethod": "save",
        "methodProperties": {
            "FirstName": "",
            "LastName": "Тестенко",
            "Phone": "invalid_phone",
            "CounterpartyType": "PrivatePerson",
            "CounterpartyProperty": "Recipient"
        }
    }
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert len(body["errors"]) > 0
def test_5_unauthorized_access_to_protected_resource():
    payload = {
        "apiKey": "00000000000000000000000000000000",  # Свідомо недійсний токен
        "modelName": "InternetDocument",
        "calledMethod": "getDocumentList",
        "methodProperties": {
            "DateTimeFrom": "01.10.2026",
            "DateTimeTo": "21.10.2026",
            "GetFullList": "1"
        }
    }
    response = requests.post(BASE_URL, json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert len(body["errors"]) > 0
    error_text = " ".join(body["errors"]).lower()
    assert "apikey" in error_text or "key" in error_text


def test_6_validation_of_tracking_number():
    payload = {
        "apiKey": API_KEY,
        "modelName": "TrackingDocument",
        "calledMethod": "getStatusDocuments",
        "methodProperties": {
            "Documents": [
                {
                    "DocumentNumber": "12345",
                    "Phone": "380500000000"
                }
            ]
        }
    }
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False or len(body["warnings"]) > 0 or len(body["errors"]) > 0
@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_7_different_http_methods(method):
    response = requests.request(method, BASE_URL)
    assert response.status_code in [200, 400, 405]
    if response.status_code == 200 and "application/json" in response.headers.get("Content-Type", ""):
        body = response.json()
        assert body["success"] is False
