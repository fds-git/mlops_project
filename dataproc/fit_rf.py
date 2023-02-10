import logging
import argparse
from datetime import datetime
from pyspark.ml.feature import OneHotEncoder
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.tuning import TrainValidationSplit
from pyspark.ml import Pipeline
import mlflow
from mlflow.tracking import MlflowClient
from pyspark.ml.classification import RandomForestClassifier
from pyspark.sql.functions import col
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

def get_pipeline():
    # числовые признаки, требующие нормализации
    columns_to_scale = ["TX_AMOUNT", "x_customer_id", "y_customer_id", "mean_amount", "std_amount", "mean_nb_tx_per_day",
                   "x_terminal_id", "y_terminal_id"]

    stages = [VectorAssembler(inputCols=[col], outputCol=col + "_vec") for col in columns_to_scale]

    # one-hot преобразование hour
    stages.append(OneHotEncoder(inputCol="hour", outputCol="hour_encoded"))

    # one-hot преобразование day_of_week
    stages.append(OneHotEncoder(inputCol="day_of_week", outputCol="day_of_week_encoded"))

    # Собираем все признаки вместе
    stages.append(VectorAssembler(inputCols=[
        "hour_encoded",
        "day_of_week_encoded",
        "TX_AMOUNT_vec",
        "x_customer_id_vec",
        "y_customer_id_vec",
        "mean_amount_vec",
        "std_amount_vec",
        "mean_nb_tx_per_day_vec",
        "x_terminal_id_vec",
        "y_terminal_id_vec"
        ],
        outputCol="Features",
    ))

    stages.append(RandomForestClassifier(numTrees=10, maxDepth=15, labelCol="TX_FRAUD", seed=42, leafCol="leafId", featuresCol='Features'))
    pipeline = Pipeline(stages=stages)

    return pipeline

def main(args):
    
    # Create Spark Session. Добавьте в название приложение оригинальное имя
    logger.info("Creating Spark Session ...")
    spark = SparkSession\
        .builder\
        .appName("fit_rand_forest")\
        .getOrCreate()

    # Load data
    logger.info("Loading Data ...")
    data_name = args.train_artifact
    data=spark.read.parquet(f'/user/processed_data/{data_name}/processed.parquet')
    train_data, valid_data = data.randomSplit([0.8, 0.2], seed=26)

    evaluator = BinaryClassificationEvaluator(labelCol="TX_FRAUD", rawPredictionCol="prediction", metricName='areaUnderPR')

    # Prepare MLFlow experiment for logging
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
    client = MlflowClient()
    experiment = client.get_experiment_by_name("Homework")
    experiment_id = experiment.experiment_id

    run_name = 'Card_fraud_random_forest' + ' ' + data_name

    with mlflow.start_run(run_name=run_name, experiment_id=experiment_id):
        inf_pipeline = get_pipeline()
        logger.info("Train model ...")
        scalerModel = inf_pipeline.fit(train_data)

        logger.info("Scoring the model ...")
        train_data = scalerModel.transform(train_data)
        valid_data = scalerModel.transform(valid_data)
        valid_roc = evaluator.evaluate(valid_data)
        train_roc = evaluator.evaluate(train_data)

        run_id = mlflow.active_run().info.run_id
        logger.info(f"Logging metrics to MLflow run {run_id} ...")
        mlflow.log_metric("train_areaUnderPR", train_roc)
        mlflow.log_metric("valid_areaUnderPR", valid_roc)
        logger.info(f"Train areaUnderPR: {train_roc}")
        logger.info(f"Valid areaUnderPR: {valid_roc}")

        logger.info("Saving model ...")
        mlflow.spark.save_model(scalerModel, args.output_artifact)

        logger.info("Exporting/logging model ...")
        mlflow.spark.log_model(scalerModel, args.output_artifact)
        logger.info("Done")

    result = valid_data.select(col("TX_FRAUD"),col("prediction")).toPandas()
    result.to_csv(f'../data/rf_pred_target.csv', index=False)
    spark.stop()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Model (Inference Pipeline) Training")

    parser.add_argument(
        "--train_artifact", 
        type=str,
        help='Fully qualified name for training artifact/dataset' 
        'Training dataset will be split into train and validation',
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name for the output serialized model (Inference Artifact folder)",
        required=True,
    )

    args = parser.parse_args()

    main(args)
