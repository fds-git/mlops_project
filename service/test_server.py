"""Модуль с юнит (модульными) и интеграционными (связка REST с моделью) тестами,
запускаемыми через pytest"""

from fastapi.testclient import TestClient
from server import app, Model, MODEL, load

# Необхадимо создать клиент и загрузить модель
client = TestClient(app)
Model.pipeline = load(MODEL)


def test_healthcheck():
    """Тестирование доступности сервера"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Green"


def test_predict():
    """Тестирование обработки одного значения"""
    transaction = {
        "TX_AMOUNT": 40.0,
        "x_customer_id": 36.5,
        "y_customer_id": 26.5,
        "mean_amount": 52.1,
        "std_amount": 26.1,
        "mean_nb_tx_per_day": 2.71,
        "x_terminal_id": 40.1,
        "y_terminal_id": 23.7,
        "day_of_week": 1,
        "hour": 0,
    }
    response = client.post("/predict", json=transaction, timeout=30)
    assert response.status_code == 200
    assert response.json() == {"isfraud":0}


def test_batch():
    """Тестирование обработки батча"""
    transactions = {
        "transactions": [
            {
                "TX_AMOUNT": 40.0,
                "x_customer_id": 36.5,
                "y_customer_id": 26.5,
                "mean_amount": 52.1,
                "std_amount": 26.1,
                "mean_nb_tx_per_day": 2.71,
                "x_terminal_id": 40.1,
                "y_terminal_id": 23.7,
                "day_of_week": 1,
                "hour": 0,
            },
            {
                "TX_AMOUNT": 400.0,
                "x_customer_id": 36.5,
                "y_customer_id": 26.5,
                "mean_amount": 52.1,
                "std_amount": 26.1,
                "mean_nb_tx_per_day": 2.71,
                "x_terminal_id": 40.1,
                "y_terminal_id": 23.7,
                "day_of_week": 5,
                "hour": 12,
            },
        ]
    }

    response = client.post("/predict_batch", json=transactions, timeout=30)
    assert response.status_code == 200
    assert response.json() == {"isfraud":[0.0,0.0]}
