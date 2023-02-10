import boto3
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net'
)

s3.upload_file('fitted_model_name.tar.gz', 'mlflowbucket', 'fitted_model_name.tar.gz')