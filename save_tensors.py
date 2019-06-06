import numpy as np
import os
from create_tensors import images_to_tensors

# classes of each output
classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

ROOT_PATH = os.getcwd()
IMAGES_PATH = 'C:\\Users\\admin\\Documents\\Uni\\vision\\MyCode'
print('starting')
train_data, train_labels = images_to_tensors(IMAGES_PATH + '\\training_data')
print('training done')
valid_data, valid_labels = images_to_tensors(IMAGES_PATH + '\\validation_data')
print('validation done')
test_data, test_labels = images_to_tensors(IMAGES_PATH + '\\test_data')
print('testing done')
os.chdir(ROOT_PATH + '\\tensors')
np.save('train_data.npy', train_data)
np.save('train_labels.npy', train_labels)
np.save('valid_data.npy', valid_data)
np.save('valid_labels.npy', valid_labels)
np.save('test_data.npy', test_data)
np.save('test_labels.npy', test_labels)
