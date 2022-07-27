import glob
import os

import matplotlib.colors as mc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearnex import patch_sklearn

patch_sklearn()

from sklearn.cluster import KMeans
from skimage.transform import rescale

img_paths = glob.glob('/mnt/d/Untitled Export/Analog/*Infrared*/*.*')
print(len(img_paths))

n_clusters = 20
dominant_color = []
colormap = np.zeros((20, 200, 3))

initial_shapes = []
last_jpg = ''

for file in img_paths:
    try:
        img = plt.imread(file)
        img = rescale(img, (0.2, 0.2, 1))
        initial_shapes.append(img.shape)

        img = img.reshape(-1, 3)
        last_jpg = file

    except Exception as e:
        print(e)
        continue

    try:
        pixel_array = np.concatenate((pixel_array, img), axis=0)
        print(pixel_array.shape)

    except NameError:
        pixel_array = img
        print(pixel_array.shape)

y_labels = KMeans(n_clusters=n_clusters, random_state=0).fit_predict(pixel_array)

color_list = []
clustered_img = np.zeros(pixel_array.shape)

for cluster in range(0, n_clusters):
    color = np.mean(pixel_array[y_labels == cluster], axis=0)
    color_list.append(color)
    clustered_img[y_labels == cluster] = color

color_label, color_frequency = np.unique(y_labels, return_counts=True)
sorting_order = np.argsort(color_frequency)

color_frequency = color_frequency[sorting_order]
color_list = np.array(color_list)[sorting_order]

index = 0
color_map = np.zeros((20, 200, 3))

adjusted_sorted_colors = []
for color in color_list:
    adjusted_sorted_colors.append(np.sqrt(.241 * color[0] + .691 * color[1] + .068 * color[2]))

order = np.argsort(adjusted_sorted_colors)
color_frequency = color_frequency[order]

idx = np.linspace(0, color_map.shape[1], len(color_list) + 1, dtype=int)

for n, color in enumerate(color_list[order]):
    color_map[:, idx[n]:idx[n + 1]] = color

hex_color = []
for color in color_list[order]:
    hex_color.append(mc.rgb2hex(color))

df = pd.DataFrame(hex_color)
with open(os.path.basename(last_jpg).replace('.jpg', '_clustered.html').replace('.JPG', '_clustered.html'), 'w') as fo:
    fo.write(df.to_html(classes=["table-bordered", "table-striped", "table-hover"]))

final_img = color_map
plt.imshow(final_img)
plt.axis('off')
plt.tight_layout()
plt.savefig(os.path.basename(last_jpg).replace('.jpg', '_clustered.png').replace('.JPG', '_clustered.png'),
            bbox_inches='tight', pad_inches=0)
plt.clf()
