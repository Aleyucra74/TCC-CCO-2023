import os
import re
import time
import boto3
import torch
import asyncio
import argparse
import datetime
import pandas as pd
from conn.connectionBoto import connection_aws

async def ultimo_objeto(conn,bucket):
    #file
    lastModified = None

    paginator = conn.get_paginator('list_objects')
    page_iterator = paginator.paginate(Bucket=bucket)

    #get the last file uploaded in s3bucket
    for page in page_iterator:
        if "Contents" in page:
            latest2 = max(page['Contents'], key=lambda x: x['LastModified'])
            if lastModified is None or latest2['LastModified'] > lastModified['LastModified']:
                lastModified = latest2
            path, filename = os.path.split(lastModified['Key'])
            if not os.path.exists(path):
                os.makedirs(path)
            conn.download_file(bucket, lastModified['Key'], lastModified['Key'])
            print(f"Downloaded:{lastModified['Key']}")
    
    path, filename = os.path.split(lastModified['Key'])

    pattern = r"\d{8}"
    match = re.search(pattern, filename)
    
    if match:
        date = match.group()
        print(date)
    else:
        print("nenhuma data encontrada")

    if lastModified != None:
        return lastModified
    return lastModified

#load models
modelWeapon = torch.hub.load('ultralytics/yolov5', 'custom', path='./MODELOS/bestgun.pt', trust_repo=True)
modelHelmet = torch.hub.load('ultralytics/yolov5', 'custom', path='./MODELOS/besthelmet.pt',trust_repo=True)
modelHoodie = torch.hub.load('ultralytics/yolov5', 'custom', path='./MODELOS/besthoodie.pt',trust_repo=True)
modelPeople = torch.hub.load('ultralytics/yolov5', 'custom', path='./MODELOS/bestperson.pt',trust_repo=True)
modelPeople.classes = 0
os.system('cls')
ultimoPredict = None

async def main(secretKey, secretAccessKey, secretToken,bucketName):        
    global ultimoPredict

    s3Client = connection_aws(secretKey,secretAccessKey,secretToken)
    models = [modelHelmet, modelHoodie, modelPeople, modelWeapon]

    ultimoModificado = await ultimo_objeto(s3Client, bucketName)

    if ultimoPredict != ultimoModificado['Key']:
        filename = ultimoModificado['Key'].split('/')[-1]
        predicts = pd.DataFrame()
        #use models
        for model in models:
            predict = model(ultimoModificado['Key'])
            df = predict.pandas().xyxy[0]
            df['filename'] = filename
            predicts = pd.concat([predicts,df], ignore_index=True)
        folder = ultimoModificado['Key'].split('/')[0]
        output_filename = filename.split('.')[0]+".csv"
        predicts.to_csv(folder+'\/'+output_filename, sep=';',index=False)
        print(predicts)
        ultimoPredict = ultimoModificado['Key']
        #save generated csv to s3 bucket
        s3Client.upload_file(
                        fr'C:\Users\alexa\Documents\BANDTEC\TCC\TCC-CCO-2023\classification\{folder}\{output_filename}',
                        "s3-data-tcc-processed",
                        f"{folder}/{output_filename}"
                    )
        print(fr'C:\Users\alexa\Documents\BANDTEC\TCC\TCC-CCO-2023\classification\{folder}\{output_filename}')
        print(f"{folder}/{output_filename}")
        print("File Uploaded to S3...")
        time.sleep(10)
    else:
        print("Nenhum arquivo adicionado recentemente...")

if __name__ == "__main__":
    while True:
        parser = argparse.ArgumentParser(description="Models Classification")
        parser.add_argument("--SK")
        parser.add_argument("--SAK")
        parser.add_argument("--ST")
        parser.add_argument("--BKT")

        args = parser.parse_args()

        asyncio.run(main(args.SK, args.SAK, args.ST, args.BKT))
