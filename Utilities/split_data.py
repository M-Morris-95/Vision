# -*- coding: utf-8 -*-
"""
Created on Thu May 23 16:07:34 2019

@author: Will's PC
"""

import os
import random
import shutil


# A R
vals = ['Q','R','S','T','U','V','W','X','Y','Z']
#vals = ['G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
vals = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
vals = ['R']

currdir = os.getcwd()
root = currdir + '\\training_data'
dest = currdir + '\\test_data'

if not os.path.isdir(dest):
    os.mkdir(dest)

random_amount = 6
for i in vals:
    root_dir = root + '\\' + i
    dest_dir = dest + '\\' + i
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)
    files = [file for file in os.listdir(root_dir)]

    for x in range(random_amount):
        file = random.choice(files)
        shutil.move(os.path.join(root_dir, file), os.path.join(dest_dir, file))
