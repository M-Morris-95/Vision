input_names = ['conv2d_1_input']
output_names = ['dense_2/Softmax']

import tensorflow as tf
import cv2
import numpy as np
from keras.preprocessing.image import img_to_array

def get_frozen_graph(graph_file):
    """Read Frozen Graph file from disk."""
    with tf.gfile.FastGFile(graph_file, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    return graph_def

def initialise_classifier(filename = './model/new_graph.pb'):
    trt_graph = get_frozen_graph(filename)

    # Create session and load graph
    tf_config = tf.ConfigProto()
    tf_config.gpu_options.allow_growth = True
    tf_sess = tf.Session(config=tf_config)
    tf.import_graph_def(trt_graph, name='')

    image_size = [1,28,28,1]

    # Get graph input size
    for node in trt_graph.node:
        if 'input_' in node.name:
            size = node.attr['shape'].shape
            image_size = [size.dim[i].size for i in range(1, 4)]
            break

    # input and output tensor names.
    input_tensor_name = input_names[0] + ":0"
    output_tensor_name = output_names[0] + ":0"

    #print("input_tensor_name: {}\noutput_tensor_name: {}".format(
    #    input_tensor_name, output_tensor_name))

    output_tensor = tf_sess.graph.get_tensor_by_name(output_tensor_name)
    return(tf_sess, input_tensor_name, output_tensor)

def create_tensor(frame):
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img = img_to_array(img)
    img = img.reshape((1, img.shape[0], img.shape[1], img.shape[2]))
    img[0, :, :, :] = (img[0, :, :, :] / 128) - 1
    return img

def classify(tf_sess, output_tensor, input_tensor_name, img):
    # classify

    tensor = create_tensor(img)

    feed_dict = {
        input_tensor_name: tensor
    }
    proba = tf_sess.run(output_tensor, feed_dict)
    idxs = np.argsort(proba[0])[::-1]

    return proba, idxs
'''

tf_sess, input_tensor_name, output_tensor = initialise_classifier()
print('Initialised classifier')

classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
           'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


img = cv2.imread('./classification_images/4.jpg')
proba, idxs = classify(tf_sess, output_tensor, input_tensor_name, img)


# print top 3 classes and their probabilities.
for i in idxs[0:3]:
    print(classes[i], proba[0][i])'''
