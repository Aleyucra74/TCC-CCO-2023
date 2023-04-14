import cv2
import numpy as np
import os, re

path = 'C://Users//aespinoza//Documents//Bandtec//TCC//test//s3-data-preprocessed-tcc//'
photographs = os.listdir(path)
listphotos=[]

for i, photo in enumerate(photographs):
    # if re.match('Explosion002_x264',photo):
    listphotos.append(cv2.imread(path+photo))

scale_percent = 320

width = int(listphotos[1].shape[1]*scale_percent / 100)
height = int(listphotos[1].shape[0]*scale_percent / 100)
dim = (width, height)

video = cv2.VideoWriter('video2.mp4',-1,1,(width,height))

for i, photo in enumerate(listphotos):
    resized_resolution = cv2.resize(listphotos[i], dim, interpolation = cv2.INTER_AREA)
    video.write(resized_resolution)

cv2.destroyAllWindows()
video.release()