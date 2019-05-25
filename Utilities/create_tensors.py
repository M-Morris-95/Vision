# -*- coding: utf-8 -*-
"""
Created on Thu May 23 14:58:56 2019

@author: Michael Morris
create data for training CNN from directory, as np.array
"""

import os
import cv2
import numpy as np
from keras.preprocessing.image import img_to_array, array_to_img

def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append(img)
    return images




def images_to_tensors(path):
    
    num_files = sum([len(files) for r, d, files in os.walk(path)])
     
    data = np.zeros([num_files,28,28,1])
    label= np.zeros([num_files])
    
    os.chdir(path)
    list_dir = [x[0] for x in os.walk(path)]
    list_dir=list_dir[1:len(list_dir)]
    k = 0
    p = 0
    
    for i in list_dir:
        images = load_images_from_folder(i)
        for j in images:
            image = cv2.cvtColor(j, cv2.COLOR_BGR2GRAY)
            image = img_to_array(image)
            data[k, :, :, :] = image
            data[k, :, :, :] = (data[k, :, :, :]/128)-1
            label[k] = int(p)
            k = k+1
        p = p+1    
    
    for i in range(len(label)):
        label[i] = int(label[i])
    return data,label

