import os
import cv2
def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append(img)
    return images
vals = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

currdir = 'C:\\Users\\admin\\Documents\\Uni\\vision\\MyCode\\classfication_images\\training_data - Copy'
k = 1000
os.chdir(currdir)
for dir in vals:
    for i in os.listdir(dir):
        os.chdir(currdir+'\\'+dir)
        #print(i)
        os.rename(i, str(k)+'.jpg')
        k=k+1
    os.chdir(currdir)


os.chdir(currdir)
for dir in vals:
    k = 1
    for i in os.listdir(dir):
        os.chdir(currdir+'\\'+dir)
        #print(i)
        os.rename(i, str(k)+'.jpg')
        k=k+1

    os.chdir(currdir)