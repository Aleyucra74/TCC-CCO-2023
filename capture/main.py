import time
import cv2
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from conn.connectionBoto import connection_aws
import saveImg as sv

def main():
    today = datetime.now().strftime('%d%m%Y')

    secretKey = ""
    secretAccessKey = ""
    secretToken = ""

    s3Client = connection_aws(secretKey,secretAccessKey,secretToken)

    timer = 0
    interval = 1  # Save one frame per second
    cam = cv2.VideoCapture('http://192.168.15.14:4747/video')
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
