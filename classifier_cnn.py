# -*- coding: utf-8 -*-
"""
Created on Thu May 23 15:28:58 2019

@author: Will's PC
"""


import cv2
import tensorflow as tf
import keras
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D, AveragePooling2D, Dropout,  Dense
from keras.models import Sequential
from keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
from keras.callbacks import ModelCheckpoint
from keras.utils import to_categorical
import numpy as np
import os
from create_tensors import images_to_tensors

# classes of each output
classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

img_width = 28
img_height = 28
num_classes = 36


path = os.getcwd()

train_data,train_labels = images_to_tensors(path + '\\training_data')
valid_data,valid_labels = images_to_tensors(path + '\\validation_data')
test_data,test_labels   = images_to_tensors(path + '\\test_data')

train_labels = to_categorical(train_labels) 
valid_labels = to_categorical(valid_labels) 
test_labels  = to_categorical(test_labels)



model = Sequential()

model.add(Conv2D(filters = 16,kernel_size = (4,4),strides = (2,2),padding = 'valid', 
                 activation ='relu',input_shape = (img_width, img_height, 1)))



model.add(Conv2D(filters = 32, kernel_size = (2,2), strides = (4,4), padding = 'valid', activation = 'relu'))

model.add(MaxPooling2D(pool_size=(3, 3), strides=None, padding='valid'))

model.add(Conv2D(filters = 64, kernel_size = (1,1), strides = (2,2), padding = 'valid', activation = 'relu'))


model.add(GlobalAveragePooling2D())


model.add(Dense(200, activation='relu'))
model.add(Dropout(0.4))
model.add(Dense(num_classes, activation='softmax'))

model.summary()


model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])


epochs = 200

checkpointer = ModelCheckpoint(filepath='Initial_CNN.hdf5', 
                               verbose=1, save_best_only=True)

model.save('Initial_CNN.hdf5')

model.load_weights('Initial_CNN.hdf5')

history = model.fit(train_data, train_labels, 
          validation_data=(valid_data, valid_labels),
          epochs=epochs, batch_size=32, callbacks=[checkpointer], verbose=1)

predictions = [np.argmax(model.predict(np.expand_dims(tensor, axis=0))) for tensor in test_data]

test_accuracy = 100*np.sum(np.array(predictions)==np.argmax(test_labels, axis=1))/len(predictions)
print('Test accuracy: %.4f%%' % test_accuracy)

os.chdir(path)

image = cv2.imread('4.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image = img_to_array(image)
image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
image[0, :, :, :] = (image[0, :, :, :]/128)-1

# classify
proba = model.predict(image)[0]
idxs = np.argsort(proba)[::-1]

# print top 3 classes and their probabilities. Seems totally random
for i in idxs[0:4]:
    print(classes[i], proba[i])

