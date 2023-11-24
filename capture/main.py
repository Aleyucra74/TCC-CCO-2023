import time
import torch
import cv2
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from conn.connectionBoto import connection_aws
import saveImg as sv

def main():
    today = datetime.now().strftime('%d%m%Y')

    secretKey = "ASIA2ZB3IAAZZHLFGCMW"
    secretAccessKey = "6BtfvpnU9IG6v9Bkr++oOXtQQ9kEGk6TdD7WYchY"
    secretToken = "FwoGZXIvYXdzEAgaDFfSzhIRGwVM3eFcpyLJAZ2kNKHyseIrjmWp342tpPHz7hN5K+o0pw6TW1fKgXmbr0NzoCPP8k28Ki7/KlBqImMth8pOWS9MDNrNJi4DnT3MRpq5GQEzzMSd/wiF6UXz+7jyEOi+NWNhecrADt2KeykefJxXfYY+S2qfnkjzZU6vltZHKFiZIorPgbsjvZk14okPMMZ1zBaV/xEv8oB2XO9rQYxQ3sRt29cQZeeCaL8tnCGgLuiWZ1V1oc4AbpSguChaEbNvHd2ZTROBWDe6AtNqxsLb6DwnEiilrP+qBjItDMfYke1Sec/9rNLSyENRBmSNKeRA65MvKp83lv+Iw1zqD1Y16KcCxdfa1/Km"

    s3Client = connection_aws(secretKey,secretAccessKey,secretToken)

    modelWeapon = torch.hub.load('ultralytics/yolov5', 'custom', path=r'../MODELOS/bestgun.pt', trust_repo=True)
    modelHelmet = torch.hub.load('ultralytics/yolov5', 'custom', path=r'../MODELOS/besthelmet.pt', trust_repo=True)
    modelHoodie = torch.hub.load('ultralytics/yolov5', 'custom', path=r'../MODELOS/besthoodie.pt', trust_repo=True)
    modelPeople = torch.hub.load('ultralytics/yolov5', 'custom', path=r'../MODELOS/bestperson.pt', trust_repo=True)
    modelPeople.classes = 0

    timer = 0
    interval = 1  # Save one frame per second
    cam = cv2.VideoCapture("http://192.168.137.85:4747/video")

    models = [modelHelmet, modelHoodie, modelPeople, modelWeapon]

    while True:
        ret,frame = cam.read()

        # for model in models:
        #      predict = model(frame)
        predict = modelPeople(frame)
        predict2 = modelHoodie(frame)
        predict3 = modelHelmet(frame)
        predict4 = modelWeapon(frame)

        df = predict.render()[0]
        df2 = predict2.render()[0]
        df3 = predict3.render()[0]
        df4 = predict4.render()[0]

        if timer == 0 or timer % interval == 0:
            cv2.imshow('Camera Feed', df)
            cv2.imshow('Camera Feed', df2)
            cv2.imshow('Camera Feed', df3)
            cv2.imshow('Camera Feed', df4)

            filename = f"frame"+datetime.now().strftime('%d%m%Y%H%M%S')
            sv.save_img(today, frame, filename)
            try:
                s3Client.upload_file(
                    fr'C:\Users\aespinoza\Documents\Bandtec\TCC\TCC-CCO-2023\capture\{today}\{filename}.jpg',
                        "s3-data-tcc-raw",
                    f"{today}/{filename}.jpg"
                )
                print(f"File uploaded: {filename}")
            except NoCredentialsError:
                print("No AWS credentials found.")
                return
            except Exception as e:
                print(fr"Error uploading file: C:\Users\aespinoza\Documents\BANDTEC\TCC\TCC-CCO-2023\capture\{today}\{filename}.jpg - {e}")
        timer += 1
        if cv2.waitKey(1) == ord('q'):
                break
    cam.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    main()
