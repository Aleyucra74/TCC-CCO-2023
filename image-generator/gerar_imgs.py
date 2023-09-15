import os
import cv2
import numpy as np

if not os.path.exists('./s3-data-preprocessed-tcc'):
    os.makedirs('s3-data-preprocessed-tcc')

cap = cv2.VideoCapture(r"C:\Users\alexa\Downloads\y2meta.net_480p-he-shot-my-arm-off-liquor-store-owner-stops-armed-robbery-by-firing-back-at-suspects.mp4")

fps = cap.get(cv2.CAP_PROP_FPS)

count=0
# running the loop 
while (cap.isOpened()): 
  
    # extracting the frames 
    ret, img = cap.read() 
    if ret == True:
        count += 1
        # converting to gray-scale 
        gray8_image = np.zeros((120, 160), dtype=np.uint8)
        gray8_image = cv2.normalize(img, gray8_image, 0, 255, cv2.NORM_MINMAX)
        gray8_image = np.uint8(gray8_image)

        # gray8_image = cv2.cvtColor(gray8_image, cv2.COLOR_BGR2GRAY)
        inferno_palette = cv2.applyColorMap(gray8_image, cv2.COLORMAP_INFERNO)
        resized_img = cv2.resize(inferno_palette, (224,224))
        if count % int(fps) == 0:
            frame_name = os.path.join('./s3-data-preprocessed-tcc', 'frame{:04d}.jpg'.format(count))
            cv2.imwrite(frame_name, resized_img)
    else:
        break

# closing the window 
cap.release()
cv2.destroyAllWindows() 