import time
import cv2
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from conn.connectionBoto import connection_aws
import saveImg as sv

def main():
    today = datetime.now().strftime('%d%m%Y')

    secretKey = "ASIA3JP3R2PLWKOVZIIR"
    secretAccessKey = "DxMKa/Ju1ZIlc/hM8PbmK3kbjI1C5ORH2fxzbUJv"
    secretToken = "FwoGZXIvYXdzEPb//////////wEaDEBIgYYtLM3eNm/8aSLHAXc/uwzEu+6WPL7GuYQLWmV/dF5pPcAMoWqYiBaYCF/4FnKmD9rrEeKPaa2tagYKVFNfRwiTrR+0ZDJCUzhupidIInpBZm9Ac7Xsrs/Bo1CxUt51DHjY538T1rDL6pSfJ0y4tVX9safT5WRlXydPjPAVt2mAjm7WMRjUJNP1fB7XM+WmP6cPdAUVdytVOPDpACAWH3FJNCIBBkEkttb+FD8ady27rm0ZFqBYb4cKzm9GTTzTq1d6JRNo85uGu3eJlbCUXJQR6jAomO/npAYyLY85Ao+UryefE/PN5YepTtGxznYIVlVe7M6wKqkn3aysSim7Q28U+QXrPNOTPQ=="

    s3Client = connection_aws(secretKey,secretAccessKey,secretToken)

    timer = 0
    interval = 1  # Save one frame per second
    cam = cv2.VideoCapture(0)
    while True:
        ret,frame = cam.read()

        cv2.imshow('Camera Feed', frame)
        if timer == 0 or timer % interval == 0:
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