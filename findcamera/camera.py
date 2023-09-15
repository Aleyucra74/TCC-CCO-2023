import cv2
import numpy as np

#cap = cv2.VideoCapture('http://192.168.15.235')
# cap = cv2.VideoCapture('rtsp://admin:#Gf37624352869@192.168.15.235/live/ch00_0')
cap = cv2.VideoCapture('rtsp://192.168.15.235/H264?ch=1&subtype=0')

while(True):
    ret, frame = cap.read()
    cv2.imshow("Frame",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()