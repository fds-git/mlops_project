"""FastAPI Titanic model inference example"""

import argparse
import requests


def main():
    """Функция-пример работы клиента с запущенным сервером"""
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-host", "--host", required=True, type=str, help="server_ip")
    argparser.add_argument(
        "-port", "--port", required=True, type=str, help="server_port"
    )
    args = argparser.parse_args()
    url = f"http://{args.host}:{args.port}"

    print(url)

    response = requests.get(url + "/", timeout=30)
    print("status code: ", response.status_code)
    print("content: ", response.content)

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
    response = requests.post(
        url + "/predict", json=transaction, timeout=30
    )
    print("status code: ", response.status_code)
    print("content: ", response.content)

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

    response = requests.post(url + "/predict_batch", json=transactions, timeout=30)
    print("status code: ", response.status_code)
    print("content: ", response.content)


if __name__ == "__main__":
    main()
