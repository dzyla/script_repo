import datetime
import os
import glob
import shutil
import tqdm
import exifread
import argparse

### Run from command line
parser = argparse.ArgumentParser(
    description='Sync photos to one folder to another and group pictures by creation date')
parser.add_argument('--i', type=str, help='Input directory', required=True)
parser.add_argument('--o', type=str, help='Output directory', required=True)
parser.add_argument('--e', type=str, help='file extension, only one accepted', required=True)
args = parser.parse_args()

def get_date_taken(path):
    ### Read file exif, using exifread, so it will work on Windows as well
    with open(path, 'rb') as fh:

        ### try to read exif
        try:
            tags = exifread.process_file(fh, stop_tag="EXIF DateTimeOriginal")
            dateTaken = tags["EXIF DateTimeOriginal"]
            return str(dateTaken)

        ### If there is no exif, use the creation date
        except Exception as e:
            return datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y:%m:%d %H:%M')


input_folder = args.i
output_folder = args.o

### Get the list of all files
files = []
for file_extension_mod in [args.e, args.e.capitalize(), args.e.lower()]:
    files = files + glob.glob(input_folder + '/**/*.{}'.format(file_extension_mod), recursive=True)

### Copy files to corresponding directories
for file in tqdm.tqdm(files):
    creation_date = get_date_taken(file)
    try:
        creation_date = creation_date.split()[0].replace(':', '')
    except IndexError:
        creation_date = '1970:01:01'.split()[0].replace(':', '')

    ### if files are in some other directory already, use this name after shooting date
    try:
        subfolder_name = creation_date + '_' + \
                         os.path.dirname(file).replace(os.path.dirname(input_folder), '').split('/')[-1]
    except:
        subfolder_name = creation_date

    destination_folder = os.path.join(output_folder, subfolder_name)

    ### Create new folder in the output directory
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder, exist_ok=True)

    ### copy file
    shutil.copy2(file, destination_folder)
