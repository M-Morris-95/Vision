
import time

import basler_cam as camera
import preprocessor_functions as preprocessor
import mainRecognition1
import cv2
import numpy as np
from load_tf_network import initialise_classifier, classify

# ------------------------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # Image capture
    cam = camera.Camera()
    time.sleep(2)

    # Preprocessor
    pre = None
    try:
        pre = preprocessor.preprocessor(28)
    except Exception as e:
        print("**Preprocessor Error**")
        print(str(e))

    print('setting up classifier')
    tf_sess, input_tensor_name, output_tensor = initialise_classifier()
    print('Initialised classifier')

    classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
               'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


    cv2.namedWindow('title', cv2.WINDOW_NORMAL)
    try:
        while True:
            start = time.time()
            image = cam.getImage()
            success, frame, box_pts = pre.locate4Squares(image)
            for i in range(len(success)):
                if success[i]:
                    cv2.drawContours(image,[box_pts[i,:,:]],0,(0,255,0),2)
                    proba, idxs = classify(tf_sess, output_tensor, input_tensor_name, frame[i,:,:,:])
                    i = idxs[0]
                    print(classes[i], proba[0][i], end = ' ' )
                    print(1/(time.time()-start))
            cv2.imshow('title', image)
            cv2.waitKey(1)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        print(str(e))

# ------------------------------------ EOF -------------------------------------