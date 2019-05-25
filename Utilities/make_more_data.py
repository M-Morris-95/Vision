# -*- coding: utf-8 -*-
"""
Created on Thu May 23 16:07:34 2019

@author: Will's PC
"""
import math
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
import cv2
import os


def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append(img)
    return images

datagen = ImageDataGenerator(
        rotation_range=10,
        width_shift_range=0.3,
        height_shift_range=0.3,
        #rescale=1./255,
        shear_range=0.3,
        zoom_range=0.3,
        horizontal_flip=True,
        fill_mode='nearest')

path = os.getcwd()
path = path +'\\training_data'
num_files = sum([len(files) for r, d, files in os.walk(path)])

os.chdir(path)
list_dir = [x[0] for x in os.walk(path)]
list_dir=list_dir[1:len(list_dir)]
k = 0
p = 0


for next_dir in list_dir:
    # i is directory
    os.chdir(next_dir)
    images = load_images_from_folder(next_dir)
    length = len(images)
    MAX = math.ceil(100/length)
    for p in range(length):
        img = images[p]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        x = img_to_array(img)  # this is a Numpy array with shape (3, 150, 150)
        x = x.reshape((1,) + x.shape)  # this is a Numpy array with shape (1, 3, 150, 150)
      
        # the .flow() command below generates batches of randomly transformed images
        # and saves the results to the `preview/` directory
        i=0
        for batch in datagen.flow(x, batch_size=1,
                                  save_to_dir=next_dir, save_prefix='yeet', save_format='jpeg'):
            i += 1
            if i > MAX:
                break  # otherwise the generator would loop indefinitely
            
    #os.chdir(path)      


