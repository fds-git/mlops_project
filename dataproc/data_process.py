import argparse
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import dayofweek
from pyspark.sql.functions import hour

if __name__=='__main__':

    parser = argparse.ArgumentParser(description="Start date increment")
    parser.add_argument("-name", dest="name", help="name", required=True, type=str)
    args = parser.parse_args()
    name = args.name
    print(f'{name}')
    print(pyspark.__version__)

    spark = SparkSession\
            .builder\
            .appName("data_processing")\
            .getOrCreate()


    customers = spark.read.csv(f'/user/testdata/{name}/customers.csv', inferSchema=True, header=True)
    terminals = spark.read.csv(f'/user/testdata/{name}/terminals.csv', inferSchema=True, header=True)
    transactions = spark.read.csv(f'/user/testdata/{name}/transactions.csv', inferSchema=True, header=True)

    # Удаляем лишние столбцы
    customers = customers.drop("available_terminals","nb_terminals")
    transactions = transactions.drop("TX_FRAUD_SCENARIO")
    transactions = transactions.drop("TX_TIME_SECONDS", "TX_TIME_DAYS")

    # Сводим все в одну таблицу
    result = transactions.join(customers, transactions.CUSTOMER_ID == customers.CUSTOMER_ID, "left")
    result = result.join(terminals, result.TERMINAL_ID == terminals.TERMINAL_ID, "left")

    # Работаем с временными признаками
    result = result.withColumn('day_of_week', dayofweek(result.TX_DATETIME))
    result = result.withColumn('hour', hour(result.TX_DATETIME))
    result = result.drop("TX_DATETIME")

    # Удаляем потенциально полезные признаки (надо проверить), чтобы не раздувать пространство
    result = result.drop("TRANSACTION_ID", "CUSTOMER_ID", "TERMINAL_ID")

    result.write.parquet(f'/user/processed_data/{name}/processed.parquet')
    spark.stop()
