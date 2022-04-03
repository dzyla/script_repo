import glob
import os
import imageio
import pyexiv2
import rawpy
from PIL import Image
from joblib import Parallel, delayed
import argparse
import time
import shutil

### Run from command line
parser = argparse.ArgumentParser(
    description='Convert RAW camera files into reduced size jpgs or reduce images in folders recursively.')
parser.add_argument('--i', type=str, help='Input directory', required=True)
parser.add_argument('--o', type=str, help='Output directory', required=True)
parser.add_argument('--d', type=int, default=1920,
                    help='Maximum dimension of a photo')
parser.add_argument('--s', type=float, default=0.4,
                    help='Maximum size in MB of a photo')
parser.add_argument('--e', type=str, help='file extension, only one accepted', required=True)
parser.add_argument('--q', type=int, default=75,
                    help='JPG save quality')
parser.add_argument('--j', type=int, default=8,
                    help='Number of parallel threads')
parser.add_argument('--m', action='store_true',
                    help='Silent (mute) mode. Show only final stats.')
parser.add_argument('--b', type=str, default=False, help='Backup dir. Provide the path of the backup dir. '
                                                         'Used to rerun the script on the same folder')
args = parser.parse_args()

### Image options
max_shape = args.d, args.d
save_quality = args.q
size_max = args.s
saved_space = 0
out_folder = args.o
file_extension = args.e
input_folder = args.i
backup_folder = args.b

### List folder with raw files
files = []
for file_extension_mod in [file_extension, file_extension.capitalize() ]:
    files = files + glob.glob(input_folder + '/**/*.{}'.format(file_extension_mod), recursive=True)


### Job definition for parallel processing
def run_job(file):
    copied = False
    folder_new = (os.path.dirname(file).replace(os.path.dirname(input_folder), out_folder)) + '/'

    ### Create a new folder if it does not exist yet
    if not os.path.exists(folder_new):
        os.makedirs(folder_new, exist_ok=True)

    path_new = folder_new + os.path.basename(file).replace(file_extension, 'jpg')

    ### Process file only if not present in the output directory or there is a backup folder
    if not os.path.exists(path_new) or args.b:

        ### Backup files
        if backup_folder:

            destination_folder = backup_folder + os.path.dirname(file)

            ### Create new folder in the output directory
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder, exist_ok=True)

            ### Create new folder in the output directory
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder, exist_ok=True)

            ### copy file to back up location
            shutil.copy2(file, destination_folder)


        ### Open file and postprocess it

        try:

            ### Optimize images
            if backup_folder:
                try:
                    im = Image.open(file)

                except Exception as e:
                    print('Error detected: {}'.format(e))

            ### convert RAWs
            else:
                with rawpy.imread(file) as raw:
                    rgb = raw.postprocess()

                im = Image.fromarray(rgb, "RGB")


            ### Check file size and shape
            im_shape = im.size

            img_size = round(float(os.path.getsize(file)) / 1E6, 2)


            ### Reduce image size if needed
            if im_shape[0] > max_shape[0] or im_shape[1] > max_shape[1]:

                ### Get metadata from the file only if going to be modified
                exif_holder = []

                try:
                    metadata = pyexiv2.ImageMetadata(file)
                    metadata.read()

                    ### Store metadata in a list
                    for tag in metadata:
                        try:
                            exif_holder.append([tag, metadata[tag].value])

                        ### not all exif fields can be processed
                        except:
                            pass

                except Exception as e:
                    print('File: {} had unreadable EXIF'.format(file))


                im.thumbnail(max_shape, Image.ANTIALIAS)
                im.save(path_new, optimize=True, quality=save_quality)
                img_size_new = round(float(os.path.getsize(path_new)) / 1E6, 2)

            else:
                try:
                    shutil.copy2(file, os.path.dirname(path_new))
                except Exception as e:
                    ### Same file exception
                    pass

                img_size_new = round(float(os.path.getsize(path_new)) / 1E6, 2)
                copied=True

            ### Write new exif
            metadata_new = pyexiv2.ImageMetadata(path_new)
            metadata_new.read()



            for element in exif_holder:
                try:
                    metadata_new[element[0]] = pyexiv2.ExifTag(element[0], element[1])

                except Exception as e:
                    pass

            metadata_new.write()

            if not args.m:
                size_diff = abs(round(img_size - img_size_new, 2))
                if not copied:
                    print('Saved {}. Saved space = {} MB.'.format(path_new, size_diff))
                else:
                    print('File already optimized, skipping.')

            return img_size - img_size_new

        except Exception as e:
            if not args.m:
                try:
                    if im.mode != 'RGB':
                        im = im.convert('RGB')
                    im.save(path_new, optimize=True, quality=save_quality)

                except Exception as e:
                    print('There was a problem with a file: {}\nError: {}'.format(file, e))

    else:
        if not args.m:
            print('File {} already exists'.format(path_new))
        return round(float(os.path.getsize(file)) / 1E6, 2) - round(float(os.path.getsize(path_new)) / 1E6, 2)


t1 = time.time()
results = Parallel(n_jobs=args.j)(delayed(run_job)(queue_element) for queue_element in files)

print('Final statistics: saved space: {} MB, took: {} s.'.format(round(sum(list(filter(None, results))), 2),
                                                                 round(time.time() - t1), 2))
