import cv2

cam = cv2.VideoCapture("http://192.168.137.228:4747/video")
while True:
    ret,frame = cam.read()

    cv2.imshow('Camera Feed', frame)
    if cv2.waitKey(1) == ord('q'):
            break
cam.release()
cv2.destroyAllWindows()