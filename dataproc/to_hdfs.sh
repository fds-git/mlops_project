# Задана в /etc/environment
cd $WORKPATH

# Считываем имя последнего сгенерированного файла (первый аргумент скрипта)
LAST_DATA_NAME=$1
#echo $LAST_DATA_NAME

# Сохраняем файл на HDFS 
hdfs dfs -copyFromLocal ./${LAST_DATA_NAME} /user/testdata/
# Удаляем локальный файл
sudo rm -r ./${LAST_DATA_NAME}
