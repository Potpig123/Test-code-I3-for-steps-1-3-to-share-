import numpy as np
import pydicom
import os
import tarfile
from io import BytesIO
import zlib
import gzip
import argparse

def readable_dicom_file(content):
	try:
		ds = pydicom.dcmread(BytesIO(content))
		expected_length = ds.Rows * ds.Columns * (ds.BitsAllocated // 8)
		if 'PixelData' in ds and len(ds.PixelData) != expected_length:
			return False
		return True
	except pydicom.errors.InvalidDicomError:
		return False


def tarfile_read(tar_dir, out_dir, type, pid, lor, wave):
	print(tar_dir, 'in process')
	with tarfile.open(tar_dir) as tars:

		try:
			members = tars.getmembers()
		except zlib.error as e1:
			print(f"Error zlib reading tar members: {e1}")
			return
		except gzip.BadGzipFile as e2:
			print(f"Error gzip reading tar members: {e2}")
			return
		
		for member in members:
			if member.isfile():
				file = tars.extractfile(member)
				if file is None:
					continue

				name = member.name[2:]
				if len(name) > 4:
					print(tar_dir, 'wrong zip name.')
					break
				name = pid + lor + wave + name + type + '.npy'
				save_dir = os.path.join(out_dir,name)
				
				content = file.read()
				if readable_dicom_file(content):
					try:
						img = pydicom.dcmread(BytesIO(content)).pixel_array
					except AttributeError:
						continue
					img -= np.min(img)
					if np.max(img) == 0:
						return
					img = (img/np.max(img)*255).astype(np.uint8)
					img = shape_check(img)
					np.save(save_dir, img)
				else:
					print(file,'cannot read')
					return



def meta_ext(txt_dir, wave, origin_dir):
	lordict = {'RIGHT':'R', 'LEFT':'L', 'THIGH':'T'}
	typedict = {'MP_LOCATOR':'ML',
				 'SAG_3D_DESS':'S3D', 
				 'COR_FISP':'CF', 
				 'COR_IW_TSE':'CIT', 
				 'COR_MPR':'CM', 
				 'PRESCRIPTION':'P', 
				 'COR_T1_3D_FLASH':'CT3F', 
				 'SAG_T2_MAP':'STM', 
				 'AX_MPR':'AM', 
				 'SAG_IW_TSE':'SIT', 
				 'SAG_T2_CALC':'STC', 
				 'AX_T1':'AT'}
	info = np.loadtxt(txt_dir, str, skiprows=1, delimiter='\t', usecols=(3, 7, 8))
	## Index:
	## 3 ~ PID
	## 7 ~ directory
	## 8 ~ type_right/left
	pids = info[:,0]
	dirs = info[:,1]
	typelors = info[:,2]
	types = ['_'.join(i.split('_')[:-1]) for i in typelors]
	lors = [i.split('_')[-1] for i in typelors]
	lors = [lordict[i] for i in lors]
	for i in range(len(info)):
		tar_dir = dirs[i]
		lor = lors[i]
		pid = pids[i]
		type = typedict[types[i]]
		tarfile_read(tar_dir, origin_dir, type, pid, lor, wave)

def type_search(txt_dir):
	types = np.loadtxt(txt_dir, str, delimiter='\t', skiprows=1, usecols=-2)
	tmp = np.unique(types)
	tmp = ['_'.join(i.split('_')[:-1]) for i in tmp]
	print(set(tmp))
	return tmp

def crop_(image,set_shape=(384,384)):
    l,h = image.shape
    l1 = (l-set_shape[0])//2
    h1 = (h-set_shape[1])//2
    l2 = l - l1
    h2 = h - h1
    image = image[l1:l2,h1:h2]
    return image

def pad_crop(image,set_shape=(384,384)):
    l,h = image.shape
    sl,sh = set_shape
    l1 = np.max((0, (sl-l)//2))
    l2 = np.max((0, sl-l-l1))
    h1 = np.max((0, (sh-h)//2))
    h2 = np.max((0, sh-h-h1))
    pad_image = np.pad(image,((l1,l2),(h1,h2)),mode='constant',constant_values=0)
    crop_image = crop_(pad_image,set_shape)
    return crop_image

def shape_check(image,set_shape=(384,384)):
    l,h = image.shape
    sl,sh = set_shape
    if l >= sl and h >= sh:
        image = crop_(image,set_shape)
        return image
    if l < sl or h < sh:
        image = pad_crop(image,set_shape)
        return image


def get_args_parser():
	parser = argparse.ArgumentParser('Dataset', add_help=False)

	parser.add_argument('--txts_dir', default='/xdisk/hongxuding/chen/Meta/30_month_files/MR_sub_ex_30month.txt',
                        help='Meta data')
	parser.add_argument('--wave', default='M30',
                        help='wave of patient')


	return parser

if __name__ == '__main__':
	args = get_args_parser()
	args = args.parse_args()
	origin_dir = '/xdisk/xiaosun/jinchengyu/Slices/'

#	txts = ['00_month_files/MR_sub_ex_00month.txt', '18_month_files/MR_sub_ex_18month.txt', '24_month_files/MR_sub_ex_24month.txt',
#		 	'30_month_files/MR_sub_ex_30month.txt', '36_month_files/MR_sub_ex_36month.txt', '48_month_files/MR_sub_ex_48month.txt',
#			'72_month_files/MR_sub_ex_72month.txt', '96_month_files/MR_sub_ex_96month.txt']

	meta_ext(args.txts_dir, args.wave, origin_dir)

#	out_dir = '/xdisk/hongxuding/jinchengyu/pngs/'
#	tars_dir = ['/xdisk/xiaosun/jinchengyu/OAI/Package_1230502/image03/48m/6.C.1/9273362/20090721/12682013.tar.gz']
#	for tar_dir in tars_dir:
#		tarfile_read(tar_dir,out_dir, type='TEST',pid='123321',lor='R', wave='M18')
