
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import csv
import numpy as np
import matplotlib.pyplot as plt
# need to import data from csv to an np.array with lat long

classes = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
               'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

unscaled_data = np.array([[0,0,0,0]])

with open('recogntionData_2.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            #print('Column names are', {", ".join(row)})
            line_count += 1
        elif line_count == 1:
            unscaled_data = np.array([[float(row[13]), float(row[14]), classes.index(row[11]), float(row[12])]])
            line_count += 1
        else:
            unscaled_data = np.append(unscaled_data, [[float(row[13]), float(row[14]), classes.index(row[11]), float(row[12])]], axis = 0)
            line_count += 1
Data = StandardScaler().fit_transform(unscaled_data[:,:2])

# #############################################################################
# Compute DBSCAN
db = DBSCAN(eps=0.25, min_samples=10).fit(Data)
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_


# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)
latlong = np.zeros([n_clusters_,2])
stddev = np.zeros([n_clusters_])
class_conf = np.zeros([35,n_clusters_])

guess = np.zeros([n_clusters_, 5])
for i in range(n_clusters_):
    temp = unscaled_data[np.where(labels==i),:]
    
    guess[i][0:2] = [np.mean(temp[0,:,0]),np.mean(temp[0,:,1])]
    guess[i][2]= (np.std(temp[0,:,0])+np.std(temp[0,:,1]))/2
    for j in range(35):
        class_only = temp[0,np.where(temp[0,:,2]==j),3]
        class_conf[j,i] = np.sum(class_only)/len(temp[0,:,0])
    
    guess[i][3] = max(class_conf[:,i])
    guess[i][4] = np.argmax(class_conf[:,i])


#print('Estimated number of clusters: %d' % n_clusters_)
#print('Estimated number of noise points: %d' % n_noise_)

# #############################################################################

# Black removed and is used for noise instead.
unique_labels = set(labels)
colors = [plt.cm.Spectral(each)
          for each in np.linspace(0, 1, len(unique_labels))]

for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = (labels == k)

    xy = unscaled_data[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=6)

    xy = unscaled_data[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=6)
    
plt.plot(guess[0,0], guess[0,1], 'o', 
         markerfacecolor=(0, 1, 0, 1), markeredgecolor='k', 
         markersize=6)
plt.plot(guess[1,0], guess[1,1], 'o', 
         markerfacecolor=(0, 1, 0, 1), markeredgecolor='k', 
         markersize=6)

circle1 = plt.Circle((latlong[1,0], latlong[1,1]), radius=stddev[1])

circle2 = plt.Circle((latlong[0,0], latlong[0,1]), radius=stddev[0])


fig = plt.gcf()
ax = fig.gca()

ax.add_artist(circle1)
ax.add_artist(circle2)
#plt.axis('square')

#plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.show()

print(guess[0][:])
print(guess[1][:])
