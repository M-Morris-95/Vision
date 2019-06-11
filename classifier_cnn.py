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
#from create_tensors import images_to_tensors

# classes of each output
classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

WIDTH = 28
HEIGHT = 28
NUM_CLASSES = 36
EPOCHS = 50
ROOT_PATH = os.getcwd()
#IMAGES_PATH = 'C:\\Users\\admin\\Documents\\Uni\\vision\\MyCode'
os.chdir(ROOT_PATH+'/tensors')
train_data = np.load('train_data.npy')
train_labels = np.load('train_labels.npy')
valid_data = np.load('valid_data.npy')
valid_labels = np.load('valid_labels.npy')
test_data = np.load('test_data.npy')
test_labels = np.load('test_labels.npy')

train_labels = to_categorical(train_labels) 
valid_labels = to_categorical(valid_labels) 
test_labels = to_categorical(test_labels)

model = Sequential()
# input: 28x28 images with 1 channel -> (28, 28, 1) tensors.
# this applies 32 convolution filters of size 3x3 each.
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(WIDTH, HEIGHT, 1)))
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(rate=0.25))

model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(rate=0.25))

model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dropout(rate=0.5))
model.add(Dense(NUM_CLASSES, activation='softmax'))

model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

os.chdir(ROOT_PATH)
history = model.fit(train_data, train_labels,
          validation_data=(valid_data, valid_labels),
          epochs=EPOCHS, batch_size=32, verbose=1)

predictions = [np.argmax(model.predict(np.expand_dims(tensor, axis=0))) for tensor in test_data]


test_accuracy = 100*np.sum(np.array(predictions) == np.argmax(test_labels, axis=1))/len(predictions)
print('Test accuracy: %.1f%%' % test_accuracy)
# Save the h5 file to path specified.

os.makedirs('./model', exist_ok=True)
model.save("./model/model.h5")





