# Задана в /etc/environment
cd $WORKPATH

# Считываем имя последнего сгенерированного файла (первый аргумент скрипта)
LAST_DATA_NAME=$1

spark-submit \
--jars mlflow-spark-1.27.0.jar \
data_process.py \
-name ${LAST_DATA_NAME}
