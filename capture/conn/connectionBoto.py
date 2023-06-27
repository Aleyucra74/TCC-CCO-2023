import boto3

def connection_aws(aws_access_key_id,aws_secret_access_key,aws_session_token):
    s3 = boto3.client(
    service_name='s3',
    region_name='us-east-1',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token
    )
    return s3