import os
import datetime
import argparse
import time

parser = argparse.ArgumentParser(
    description='Long exposure with libcamera')
parser.add_argument('--o', type=str, help='output folder', default='/home/pi/Images/')
parser.add_argument('--t', type=int, default=30,
                    help='exposition time')
parser.add_argument('--g', type=int, default=5,
                    help='gain')

args = parser.parse_args()

folder = '{}/{}/'.format(args.o,datetime.datetime.now().strftime("%y%m%d"))
os.makedirs(folder, exist_ok=True)
print('Saving to {}'.format(folder))


while True:
	filename = folder + datetime.datetime.now().strftime("%y%m%d_%H%M%S") + '.jpg'
	os.system(
		'libcamera-still --shutter {} --gain {} --awbgains 2.2,2.3 --immediate -o {}'.format(float(args.t) * 1000000, args.g, filename))
