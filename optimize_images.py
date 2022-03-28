import glob
import os
import imageio
import pyexiv2
import rawpy
from PIL import Image
from joblib import Parallel, delayed
import argparse

parser = argparse.ArgumentParser(
    description='Convert RAW camera files into reduced size jpgs recursively.')
parser.add_argument('--i', type=str, help='Input directory', required=True)
parser.add_argument('--o', type=str, help='Output directory', required=True)
parser.add_argument('--d', type=int, default=1600,
                    help='Maximum dimension of a photo')
parser.add_argument('--s', type=float, default=0.3,
                    help='Maximum size in MB of a photo')
parser.add_argument('--e', type=str, help='file extension, only one accepted', required=True)
parser.add_argument('--q', type=int, default=60,
                    help='JPG save quality')
args = parser.parse_args()


### Image options
max_size = args.d, args.d
save_quality = args.q
size_max = args.s
saved_space = 0
backup_folder = args.o
file_extention = args.e
input_folder = args.i

### Folder with raw files
files = glob.glob(input_folder+'/**/*.{}'.format(file_extention), recursive=True)


### Job definition for parallel processing
def run_job(file):

    folder_new = (os.path.dirname(file).replace(input_folder, backup_folder))+'/'

    ### Create a new folder if it does not exist yet
    if not os.path.exists(folder_new):
        os.makedirs(folder_new, exist_ok=True)

    path_new = folder_new+os.path.basename(file).replace(file_extention, 'jpg')

    ### Process file only if not present in the output directory
    if not os.path.exists(path_new):

        ### Get metadata from the file
        metadata = pyexiv2.ImageMetadata(file)
        metadata.read()

        ### Store metadata in a list
        exif_holder = []
        for tag in metadata:
            try:
                exif_holder.append([tag, metadata[tag].value])

            ### not all exif fields can be processed
            except:
                pass

        ### Open Raw file and postprocess it
        with rawpy.imread(file) as raw:
            rgb = raw.postprocess()

        ### Check file size and shape
        im = Image.fromarray(rgb, "RGB")
        im_shape = im.size
        img_size = round(float(os.path.getsize(file)) / 1E6, 2)

        ### Reduce image size if needed
        if img_size > size_max:
            if im_shape[0] > max_size[0] or im_shape[1] > max_size[1]:
                im.thumbnail(max_size, Image.ANTIALIAS)
                im.save(path_new, optimize=True, quality=save_quality)
                img_size_new = round(float(os.path.getsize(path_new)) / 1E6, 2)
            else:
                im.save(path_new, optimize=True, quality=save_quality)
                img_size_new = round(float(os.path.getsize(path_new)) / 1E6, 2)
        else:
            img_size_new = round(float(os.path.getsize(path_new)) / 1E6, 2)

        ### Write new exif
        metadata_new = pyexiv2.ImageMetadata(path_new)
        metadata_new.read()

        for element in exif_holder:
            try:
                metadata_new[element[0]] = pyexiv2.ExifTag(element[0], element[1])

            except Exception as e:
                pass

        metadata_new.write()
        print('Saved {}. Saved space = {} MB.'.format(path_new, round(img_size-img_size_new,2)))

        return img_size - img_size_new

    else:
        print('File {} already exists'.format(path_new))



results = Parallel(n_jobs=12)(delayed(run_job)(queue_element) for queue_element in files)