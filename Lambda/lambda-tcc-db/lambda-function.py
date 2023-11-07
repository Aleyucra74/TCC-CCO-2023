import redundancia
import rekog
import os

def lambda_handler(event, context):
    
    bucket_rekog = os.environ.get('BUCKET_REKOG')
    bucket_redundancia =  os.environ.get('BUCKET_REDUNDANCIA')
    
    print(event)

    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    
    print("Nome do Bucket:", bucket_name)

    if bucket_name == bucket_rekog:
        return rekog.envio_rekog(bucket_rekog)
    else:
        return redundancia.envio_redundancia(bucket_redundancia)
