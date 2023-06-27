import os
import boto3
import torch
import datetime

aws_access_key_id = 'SECRET_KEY_ID'
aws_secret_access_key = 'SECRET_ACCESS_KEY'
aws_session_token= 'SESSION_TOKEN'
bucket_name = 's3-data-raw-tcc'

today = datetime.now().strftime('%Y-%m-%d')

s3 = boto3.client('s3', region_name="us-east-1", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)

paginator = s3.get_paginator('list_objects')
page_iterator = paginator.paginate(Bucket=bucket_name)

