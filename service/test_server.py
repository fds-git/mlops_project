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
    passenger = {
        "Name": "John",
        "Pclass": 1,
        "Sex": "male",
        "Age": 27,
        "Embarked": "S",
        "Fare": 100,
        "SibSp": 0,
        "Parch": 0,
        "Ticket": "C101",
        "Cabin": "ST",
    }

    response = client.post("/predict?passenger_id=1", json=passenger, timeout=30)
    assert response.status_code == 200
    assert response.json() == {"passenger_id": 1, "survived": 0}


def test_batch():
    """Тестирование обработки батча"""
    passengers = {
        "passengers": [
            {
                "Name": "John",
                "Pclass": 1,
                "Sex": "male",
                "Age": 27,
                "Embarked": "S",
                "Fare": 100,
                "SibSp": 0,
                "Parch": 0,
                "Ticket": "C101",
                "Cabin": "ST",
            },
            {
                "Name": "Anna",
                "Pclass": 1,
                "Sex": "female",
                "Age": 27,
                "Embarked": "S",
                "Fare": 100,
                "SibSp": 0,
                "Parch": 0,
                "Ticket": "C101",
                "Cabin": "ST",
            },
        ]
    }

    response = client.post("/predict_batch", json=passengers, timeout=30)
    assert response.status_code == 200
    assert response.json() == {"survived": [0, 1]}
