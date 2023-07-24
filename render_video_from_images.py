import imageio
import glob
from skimage import transform
from skimage.util import img_as_ubyte
import os

scale = 0.4
folder = '230722*.jpg'
out_ext = 'gif'
fps = 4
files = sorted(glob.glob(folder))

# Create a new list of files that includes the original sequence and its reverse
# Exclude the last file in the reversed sequence to avoid repeating it
files_yoyo = files + files[-2::-1]

output_filename = os.path.basename(files[0]).replace('jpg', out_ext)

# Modify output file extension to .mp4 and specify fps
if out_ext=='mp4':
    writer = imageio.get_writer(output_filename, fps=fps)
elif out_ext=='gif':
    writer = imageio.get_writer(output_filename, duration=int(1000/fps))

for file in files_yoyo:
    img = imageio.imread(file)

    if len(img.shape) == 2:  # Grayscale image
        img = transform.rescale(img, (scale, scale))  # No third dimension to scale
    elif len(img.shape) == 3:  # RGB image
        img = transform.rescale(img, (scale, scale, 1))  # Scale height and width, but not channels

    # Convert the rescaled float64 image to 8-bit unsigned integer type
    img = img_as_ubyte(img)

    writer.append_data(img)

writer.close()
