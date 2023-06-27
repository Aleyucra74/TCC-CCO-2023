import os
import cv2

def save_img(folder, frame, img_name):
    # verify if folder is create
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    filename = f"{folder}/{img_name}.jpg"
    cv2.imwrite(filename, frame)