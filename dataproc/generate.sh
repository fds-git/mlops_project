#echo ******Hello World from AWS EC2 Instance*******
#echo $(hostname -i)
cd $WORKPATH
#echo $(pwd)

# Стартовую дату для генерации данных считываем из файла
START_DATE=`cat ../data/date.txt`

# Остальные параметры для генерации задаются здесь
INCREMENT_DAYS_INTERVAL=7
CUSTOMERS=500
TERMINALS=100
RADIUS=5

# Логируем часть параметров
#echo Start generate data from $START_DATE
#echo Increment days interval $INCREMENT_DAYS_INTERVAL

# Генерируем новые данные
LAST_DATA_NAME=`python3 generate.py -c ${CUSTOMERS} -t ${TERMINALS} -d ${INCREMENT_DAYS_INTERVAL} -date ${START_DATE} -r ${RADIUS}`

# Рассчитываем стартовую дату для следующей итерации и сохраняем в файл (эта дата будет оспользоваться следующим экземпляром DAG)
NEW_DATE=`python3 increment_date.py -d ${INCREMENT_DAYS_INTERVAL} -date ${START_DATE}`
echo ${NEW_DATE} > ../data/date.txt

# Возвращаем имя сгенерированного файла для передачи следующим таскам Airflow через Xcom
echo ${LAST_DATA_NAME}


