from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import csv
import numpy as np
import matplotlib.pyplot as plt



def clustering(unscaled_data):
    Data = StandardScaler().fit_transform(unscaled_data[:, :2])
    # #############################################################################
    # Compute DBSCAN
    db = DBSCAN(eps=0.25, min_samples=10).fit(Data)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    # n_noise_ = list(labels).count(-1)
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    class_conf = np.zeros([35, n_clusters_])
    guess = np.zeros([n_clusters_, 6])

    for i in range(n_clusters_):
        temp = unscaled_data[np.where(labels == i), :]

        guess[i][0:2] = [np.mean(temp[0, :, 0]), np.mean(temp[0, :, 1])]
        guess[i][2] = (np.std(temp[0, :, 0]) + np.std(temp[0, :, 1])) / 2

        for j in range(35):
            class_only = temp[0, np.where(temp[0, :, 2] == j), 3]
            class_conf[j, i] = np.sum(class_only) / len(temp[0, :, 0])

        guess[i][3] = max(class_conf[:, i])
        guess[i][4] = np.argmax(class_conf[:, i])
        guess[i][5] = len(temp[0,:,0])
    return guess