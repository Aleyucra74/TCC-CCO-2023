import os
import boto3
import torch
import datetime
import pandas as pd
from conn.connectionBoto import connection_aws

def main():        

    secretKey = ""
    secretAccessKey = "
    secretToken = ""
    bucketName = "s3-data-tcc-raw"

    s3Client = connection_aws(secretKey,secretAccessKey,secretToken)

    #load models
    modelWeapon = torch.hub.load('ultralytics/yolov5', 'custom', path='./MODELOS/bestgun.pt', trust_repo=True)
    modelHelmet = torch.hub.load('ultralytics/yolov5', 'custom', path='./MODELOS/besthelmet.pt',trust_repo=True)
    modelHoodie = torch.hub.load('ultralytics/yolov5', 'custom', path='./MODELOS/besthoodie.pt',trust_repo=True)

    modelPeople = torch.hub.load('ultralytics/yolov5', 'custom', path='./MODELOS/bestperson.pt',trust_repo=True)
    modelPeople.classes = 0

    models = [modelHelmet, modelHoodie, modelPeople, modelWeapon]

    paginator = s3Client.get_paginator('list_objects')
    page_iterator = paginator.paginate(Bucket=bucketName)

    #get the last file uploaded in s3bucket
    lastModified = None
    for page in page_iterator:
        if "Contents" in page:
            latest2 = max(page['Contents'], key=lambda x: x['LastModified'])
            if lastModified is None or latest2['LastModified'] > lastModified['LastModified']:
                lastModified = latest2
            path, filename = os.path.split(lastModified['Key'])
            if not os.path.exists(path):
                os.makedirs(path)
            s3Client.download_file(bucketName, lastModified['Key'], lastModified['Key'])
            print(f"Downloaded:{lastModified['Key']}")
    
    predicts = pd.DataFrame()
    #use models
    for model in models:
        predict = model(lastModified['Key'])
        df = predict.pandas().xyxy[0]
        df['filename'] = lastModified['Key']
        predicts = predicts.append(df, ignore_index=True)
        print(predicts)

    predicts.to_csv(lastModified['Key'].split('/')[1]+".csv", sep=';',index=False)
    #save generated csv to s3 bucket
    # s3-data-tcc-processed
    #not working
    s3Client.upload_file(
                    fr'C:\Users\alexa\Documents\BANDTEC\TCC\TCC-CCO-2023\classification\{lastModified['Key'].split('/')[1]}.csv',
                     "s3-data-tcc-processed",
                    f"{today}/{filename}.jpg"
                )

if __name__ == "__main__":
    main()
