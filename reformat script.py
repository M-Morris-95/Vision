import cv2
import os
from functions import preprocess
import shutil
import numpy as np

dir = '1'

def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append(img)
    return images
vals = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
currdir = os.getcwd()
for dir in vals:

    os.chdir(currdir + '\\Folders')
    images = load_images_from_folder(dir)
    k=0
    os.chdir(currdir + '\\training_data')

    os.mkdir(os.getcwd() + '\\' +dir)
    os.chdir(os.getcwd() + '\\' +dir)

    neg = np.zeros([28,28,3])
    for i in images:
        img = preprocess(i)
        cv2.imwrite(str(k)+'.jpg',img)
        k = k+1

