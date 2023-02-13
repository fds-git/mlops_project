"""Бэкенд инференса модели на FastAPI"""

from typing import Optional, List
import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.pipeline import Pipeline
import mlflow

app = FastAPI()

MODEL = os.getenv("MODEL", default="./fitted_model_name")


def load(path: str):
    """Функция загрузки обученной модели"""
    return mlflow.pyfunc.load_model(path)


class Model:
    """Класс, для работы с обученной моделью"""

    pipeline: Optional[Pipeline] = None


class Transaction(BaseModel):
    """Класс, формирующий структуру данных для единичного предсказания"""

    TX_AMOUNT: float
    x_customer_id: float
    y_customer_id: float
    mean_amount: float
    std_amount: float
    mean_nb_tx_per_day: float
    x_terminal_id: float
    y_terminal_id: float
    day_of_week: int
    hour: int


class TransactionList(BaseModel):
    """Класс, формирующий структуру данных для batch предсказания"""

    transactions: List[Transaction]


@app.on_event("startup")
def load_model():
    """Загрузка модели. Производится при запуске сервера"""
    Model.pipeline = load(MODEL)


@app.get("/")
def read_healthcheck():
    """Проверка доступности сервера"""
    return {"status": "Green", "version": "0.2.0"}


@app.post("/predict")
def predict(transaction: Transaction):
    """Функция предсказания одного значения
    Входные параметры:
    transaction: Transaction - информация о транзакции (JSON)"""
    dataframe = pd.DataFrame([transaction.dict()])
    dataframe.fillna(value=np.nan, inplace=True, downcast=False)
    if Model.pipeline is None:
        raise HTTPException(status_code=503, detail="No model loaded")
    try:
        pred = int(Model.pipeline.predict(dataframe)[0])
    except Exception as exept:
        raise HTTPException(status_code=400, detail=str(exept))

    return {"isfraud": pred}


@app.post("/predict_batch")
def predict_batch(transactions: TransactionList):
    """Функция предсказания значений для батча
    Входные параметры:
    transactions: TransactionList - информация о транзакциях (JSON[LIST[JSON]])"""
    data = transactions.dict()["transactions"]
    dataframe = pd.DataFrame(data)
    dataframe.fillna(value=np.nan, inplace=True, downcast=False)
    if Model.pipeline is None:
        raise HTTPException(status_code=503, detail="No model loaded")
    try:
        pred = Model.pipeline.predict(dataframe)  # .tolist()
    except Exception as exept:
        raise HTTPException(status_code=400, detail=str(exept))

    return {"isfraud": pred}
