import cv2
import os
import preprocessor_functions as preprocessor
import shutil
import numpy as np

pre = preprocessor.preprocessor( 28 )

currdir = 'C:\\Users\\admin\\Documents\\Uni\\vision\\MyCode\\classfication_images\\flight pics'
os.chdir(currdir)
print("loaded images")
k=0
for filename in os.listdir(currdir):

    img = cv2.imread(os.path.join(currdir, filename))
    found, image, rect = pre.locateSquare(img)
    if found:
        os.chdir(currdir + '\\reformatted')
        cv2.imwrite(str(k) + '.jpg', image)
        os.chdir(currdir)
        k = k + 1
        print(k)

