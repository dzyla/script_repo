import imageio
import glob
from skimage import transform

files = sorted(glob.glob('2021-08-12*.jpg'))

### This will require imageio-ffmpeg
writer = imageio.get_writer('2021-08-12.mp4', fps=4)

for file in files:
    img = imageio.imread(file)

    ### scale image (1,1,1) means no scaling, (1,1) drops channels
    img = transform.rescale(img, (0.3, 0.3, 1))

    writer.append_data(img)

writer.close()