import time
import torch
import cv2
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from conn.connectionBoto import connection_aws
import saveImg as sv

def main():
    today = datetime.now().strftime('%d%m%Y')

    secretKey = "ASIA2ZB3IAAZQ6BBEV6C"
    secretAccessKey = "tpw3mbYey1gV9C7ICtZlqI9pSQ1m48B8BNxJKfR+"
    secretToken = "FwoGZXIvYXdzEDYaDEbMWJfF4el7jjIGMSLJAR+0BWF9rUICGVokq4XneeoR7JB9UCTS8fCSbZtmX7d3gBmLifLdL1s4hlZUWBwgKGvDwuBabRWKi4zxJU01e71DfqW9yJq4dVquXR1UN0xDD3dPFRxvBO5iHAyPVDGKG94jy7uDOPG7a8rVUDpWh+JWvCDk7sm7gU1msbUkE2QTUE+yh5tvim6i7eyr/ojhtOCorzgd7vB8R2eVFPhvjUBsscx8dMJ77mSXlag7L1iq7nzphtQ+phwPnGUWmRjCIRCuqVJGA9ktESjAt4mrBjItMXRCLiiaqMf1k0Bfnjz9FsH0S3DYHxmiaDvIik57KxLj5hQhDc2vwLOoseTN"

    s3Client = connection_aws(secretKey,secretAccessKey,secretToken)

    modelALL = torch.hub.load('ultralytics/yolov5', 'custom', path=r'../MODELOS/best.pt', trust_repo=True)

    timer = 0
    interval = 1  # Save one frame per second
    # cam = cv2.VideoCapture("http://192.168.15.29:4747/video")
    cam = cv2.VideoCapture(0)

    while True:
        ret,frame = cam.read()

        # for model in models:
        #      predict = model(frame)
        if timer == 0 or timer % interval == 0:
            predict = modelALL(frame)
            df = predict.render()[0]
            cv2.imshow('Camera Feed', df)

            filename = f"frame"+datetime.now().strftime('%d%m%Y%H%M%S')
            sv.save_img(today, frame, filename)
            try:
                s3Client.upload_file(
                    fr'C:\Users\alexa\Documents\BANDTEC\TCC\TCC-CCO-2023\capture\{today}\{filename}.jpg',
                        "s3-data-tcc-raw",
                    f"{today}/{filename}.jpg"
                )
                print(f"File uploaded: {filename}")
            except NoCredentialsError:
                print("No AWS credentials found.")
                return
            except Exception as e:
                print(fr"Error uploading file: C:\Users\alexa\Documents\BANDTEC\TCC\TCC-CCO-2023\capture\{today}\{filename}.jpg - {e}")
        timer += 1
        if cv2.waitKey(1) == ord('q'):
                break
    cam.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    main()
