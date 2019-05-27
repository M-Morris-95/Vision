# -*- coding: utf-8 -*-
"""
Created on Thu May 23 15:28:58 2019

@author: Will's PC
"""


import cv2
import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.optimizers import SGD
from keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
from keras.callbacks import ModelCheckpoint
from keras.utils import to_categorical
import numpy as np
import os
from create_tensors import images_to_tensors
import time

# classes of each output
classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

WIDTH = 28
HEIGHT = 28
NUM_CLASSES = 36
EPOCHS = 0
ROOT_PATH = os.getcwd()
IMAGES_PATH = 'C:\\Users\\admin\\Documents\\Uni\\vision\\MyCode'

test_data, test_labels = images_to_tensors(IMAGES_PATH + '\\test_data2')
test_labels = to_categorical(test_labels)
os.chdir(ROOT_PATH)

model = Sequential()
# input: 28x28 images with 1 channel -> (28, 28, 1) tensors.
# this applies 32 convolution filters of size 3x3 each.
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(WIDTH, HEIGHT, 1)))
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dense(NUM_CLASSES, activation='softmax'))

model.load_weights('weights.hdf5')
start = time.time()
predictions = [np.argmax(model.predict(np.expand_dims(tensor, axis=0))) for tensor in test_data]
print(time.time()-start)
test_accuracy = 100*np.sum(np.array(predictions) == np.argmax(test_labels, axis=1))/len(predictions)
print('Test accuracy: %.1f%%' % test_accuracy)




