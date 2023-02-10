import boto3
import os

print(os.getenv('aws_access_key_id'))
print(os.getenv('aws_secret_access_key'))
print(os.getenv('region'))

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id = os.getenv('aws_access_key_id'),
    aws_secret_access_key = os.getenv('aws_secret_access_key'),
    #region = os.getenv('region')
)

s3.download_file('mlflowbucket', 'fitted_model_name.tar.gz', 'fitted_model_name.tar.gz')