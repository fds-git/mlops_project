from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.ssh.hooks.ssh import SSHHook
from datetime import datetime, timedelta
from airflow.models import Variable
import base64
from airflow.operators.python import PythonOperator

# minutes=2 - чтобы скрипт точно запустился
default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(minutes=10)
}

# Результат функции можно будет получить через Xcom
def _decode_message(task_name, ti):
    message = ti.xcom_pull(task_ids=task_name)
    return base64.b64decode(message).decode()

# Загружаем переменные окружения
DATAPROC_IP = Variable.get("DATAPROC_IP")
DATAPROC_PORT = Variable.get("DATAPROC_PORT")
USERNAME = Variable.get("USERNAME")
KEY_FILE = Variable.get("KEY_FILE")
WORKPATH = Variable.get("WORKPATH")

# Данное выражение, добавленное в ssh (bash) команду, извлечет XCOM из заданной таски,
# далее этот XCOM можно передавать как параметр в этой же команде
EXPRESSION_TO_GET_XCOM = '{{ ti.xcom_pull(task_ids="decode_generated_file_name") }}'

sshHook = SSHHook(
    remote_host=DATAPROC_IP, 
    port=DATAPROC_PORT, 
    username=USERNAME, 
    key_file=KEY_FILE, timeout=1000
)

generate_command = f'bash {WORKPATH}/generate.sh '
to_hdfs_command = f'bash {WORKPATH}/to_hdfs.sh {EXPRESSION_TO_GET_XCOM}'
process_command = f'bash {WORKPATH}/data_process.sh {EXPRESSION_TO_GET_XCOM}'
fit_rand_for_command = f'bash {WORKPATH}/fit_rf.sh {EXPRESSION_TO_GET_XCOM}'
upload_model_command = f'bash {WORKPATH}/upload_model.sh '
redeploy_command = f'bash {WORKPATH}/redeploy.sh '


with DAG('pipeline',
    schedule_interval='*/5 * * * *' ,
    default_args=default_args
    ) as dag:

    generate_task = SSHOperator(
    ssh_hook=sshHook,
    task_id='generate_data',
    command=generate_command,
    cmd_timeout=100
    )

    # Название сгенерированного файла надо декодировать
    # для передачи следующим таскам
    decoder = PythonOperator(
    task_id='decode_generated_file_name',
    python_callable=_decode_message,
    op_args=['generate_data'],
    )

    to_hdfs_task = SSHOperator(
    ssh_hook=sshHook,
    task_id='data_to_hdfs',
    command=to_hdfs_command
    )

    process_task = SSHOperator(
    ssh_hook=sshHook,
    task_id='process_data',
    command=process_command
    )

    fit_rand_forest_task = SSHOperator(
    ssh_hook=sshHook,
    task_id='fit_rand_forest',
    command=fit_rand_for_command,
    conn_timeout=1000,
    cmd_timeout=1000
    )

    upload_model_task = SSHOperator(
    ssh_hook=sshHook,
    task_id='upload_model_s3',
    command=upload_model_command
    )

    redeploy_task = SSHOperator(
    ssh_hook=sshHook,
    task_id='redeploy_model',
    command=redeploy_command
    )

    generate_task >> decoder >> to_hdfs_task >> process_task >> fit_rand_forest_task >>\
        upload_model_task >> redeploy_task
