import time
import cv2
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from conn.connectionBoto import connection_aws
import saveImg as sv

def main():
    today = datetime.now().strftime('%d%m%Y')

    secretKey = "ASIA3JP3R2PLVLBJAZYL"
    secretAccessKey = "RBpyWIz8n8prZnB0TI0DJ3RPRALlOdQmtN9i0vb3"
    secretToken = "FwoGZXIvYXdzEAsaDJjZb3XkV4ti/hS91CLHAW3V9Wnf/0UQRrDy/QP9vcID34bQqqkzctc8b7rgPXMRGvQFKQcHDo9onN39FVTlctXTnq82UqbkUt0XXEveiuVoLtxMA9GLg28MGyZ+0LupxU5SNRphWl4SrcHG3Y23e0hY8UzqtnkIchnjgD2eTk1Zdepe8ZV+BQyW6dkIzZ2OiwkTJIAAYNlvS+f8di1L9aO4H0+5PrQg6B/WYzDbLNxNx/uMo5WUxTWU9BgHtL0pgmXLytvyEvy9CzGalZdnMYa+Owsm7MMoy7fspAYyLdaDY6xkLwdSwojCEPT5/eJDkRmMjL3KHC7+devLOtaAIAWnmgTvJcbSTVU78g=="

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