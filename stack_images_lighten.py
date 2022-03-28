import os.path
import matplotlib.pyplot as plt
import numpy as np
import tqdm
import glob
import imageio
plt.ion()

def avg_img(img):
    avg = np.average(img)
    return avg

def max_imgs(img1, img2):
    max_ = np.maximum(img1, img2)
    return max_

### Get the files from the directory, in the sorted manner
files = sorted(glob.glob('H:\\night_sky\\2021-08-12\\*.jpg'))

output_name = os.path.basename(os.path.dirname(files[0]))
print('Found {} images'.format(len(files)))

first_file = True

### For keeping the average photo exposure
average = []

for n, file in tqdm.tqdm(enumerate(files)):

    ### For the first image just load it
    if first_file:
        stack = imageio.imread(file).astype(float)
        average_intensity = avg_img(stack)

        first_file = False

    ### Calculate maximum projection between the previous image and next
    else:
        img =  imageio.imread(file)

        average_intensity = avg_img(stack)
        average.append(average_intensity)

        stack = max_imgs(stack, img)


    ### Save maximum projection every n images
    if n%50 == 0 and n != 0:

        ### Save file with leading zeros
        imageio.imsave('{}_{}.jpg'.format(output_name,f"{n:04d}"), stack.astype(np.uint8))

    plt.plot(range(0, len(average)), average)
    plt.show()
    plt.pause(0.0001)
    plt.cla()

imageio.imsave('{}_final.jpg'.format(output_name), stack.astype(np.uint8))

### Plot the average intensity statistics per image
plt.plot(range(0, len(average)), average)
plt.xlabel('Image number')
plt.ylabel('Average Intensity')
np.save('{}_average_light.npy'.format(output_name), np.array(average))
plt.savefig('{}_average_light.png'.format(output_name))