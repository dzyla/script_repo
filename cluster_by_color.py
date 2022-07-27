import glob
import os
import shutil

import imageio as io
import matplotlib.pyplot as plt
import numpy as np
from sklearnex import patch_sklearn

patch_sklearn()

from sklearn.cluster import KMeans
from skimage.transform import rescale

img_paths = glob.glob('/mnt/d/Analog/**/*.*')
n_clusters = 10
dominant_color = []
colormap = np.zeros((20, 200, 3))

# Make the list of processed images
processed_files_ = glob.glob('./annoteted_imgs/*.*')
processed_files = []
for file in processed_files_:
    processed_files.append(os.path.basename(file))


for file_n, file in enumerate(img_paths):

    # Process new files only and if size is less than 40 MB
    if os.path.getsize(file)/1e6 < 40 and '{}_{}'.format(file_n,
    os.path.basename(file).replace('.jpg', '_clustered.png').replace('JPG', '_clustered.png')) not in processed_files:
        try:
            img = io.imread(file)
        except Exception as e:
            print(file)
            print(e)
            continue
    else:
        print(file)
        continue

    try:
        img = rescale(img, (0.3, 0.3, 1))
        initial_shape = img.shape

        img = img.reshape(-1, 3)
        print(initial_shape)

    except Exception as e:
        print(e)
        print(file)
        continue

    y_labels = KMeans(n_clusters=n_clusters, random_state=0).fit_predict(img)

    color_list = []
    clustered_img = np.zeros(img.shape)

    for cluster in range(0, n_clusters):
        color = np.mean(img[y_labels == cluster], axis=0)
        color_list.append(color)
        clustered_img[y_labels == cluster] = color


    color_label, color_frequency = np.unique(y_labels, return_counts=True)
    sorting_order = np.argsort(color_frequency)

    color_frequency = color_frequency[sorting_order]
    color_list = np.array(color_list)[sorting_order]

    index = 0
    color_map = np.zeros((20, initial_shape[1],3))

    for n, color in enumerate(color_list):
        fraction = int(initial_shape[1] * (color_frequency[n] / img.shape[0]))
        if n < len(color_frequency) - 1:
            color_map[:, index:index + fraction] = color
        else:
            color_map[:, index:] = color
            dominant_color.append(color)
        index = index + fraction

    white_spacer = np.ones((5, initial_shape[1], 3))
    final_img = np.concatenate((color_map, white_spacer, clustered_img.reshape(initial_shape)), axis=0)
    plt.imshow(final_img)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('./annoteted_imgs/{}_{}'.format(file_n,
                        os.path.basename(file).replace('.jpg', '_clustered.png').replace('JPG', '_clustered.png')),
                        bbox_inches='tight', pad_inches=0)
    plt.clf()


adjusted_sorted_colors = []
for color in dominant_color:
    adjusted_sorted_colors.append(np.sqrt(.241 * color[0] + .691 * color[1] + .068 * color[2]))

color_map = colormap
idx = np.linspace(0, color_map.shape[1], len(dominant_color) + 1, dtype=int)

img_order = np.argsort(adjusted_sorted_colors)

for n, color in enumerate(np.array(dominant_color)[img_order]):
    color_map[:, idx[n]:idx[n + 1]] = color

plt.imshow(color_map)
plt.axis('off')
plt.tight_layout()
plt.savefig('color_by_image.png', bbox_inches='tight', pad_inches=0)


for n, color in enumerate(np.array(dominant_color)):
    color_map[:, idx[n]:idx[n + 1]] = color

plt.imshow(color_map)
plt.axis('off')
plt.tight_layout()
plt.savefig('color_by_image_unsorted.png', bbox_inches='tight', pad_inches=0)

os.makedirs('sorted_imgs', exist_ok=True)
for n, file in enumerate(img_paths):
    shutil.copy2(file, './{}/{}_{}'.format('sorted_imgs', img_order[n], os.path.basename(file)))
