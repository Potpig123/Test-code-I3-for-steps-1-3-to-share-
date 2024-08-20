import numpy as np
import pydicom
import matplotlib.pyplot as plt
import os
import tarfile
from io import BytesIO


def readable_dicom_file(content):
	try:
		ds = pydicom.dcmread(BytesIO(content))
		expected_length = ds.Rows * ds.Columns * (ds.BitsAllocated // 8)
		if 'PixelData' in ds and len(ds.PixelData) != expected_length:
			return False
		return True
	except pydicom.errors.InvalidDicomError:
		return False


def tarfile_read(tar_dir, out_dir, pid, lor, wave):
	with tarfile.open(tar_dir) as tars:
		for member in tars.getmembers():
			if member.isfile():
				print(member)
				print(member.name)
				file = tars.extractfile(member)
				content = file.read()
				name = member.name[2:]
				name = pid + lor + wave + name + '.npy'
				save_dir = os.path.join(out_dir,name)
				if readable_dicom_file(content):
					img = pydicom.dcmread(BytesIO(content)).pixel_array
					img -= np.min(img)
					img = (img/np.max(img)*255).astype(np.uint8)
					np.save(save_dir, img)
					print(name, 'saved')
				else:
					print(file,'cannot read')
					return
		
def meta_ext(txt_dir, wave, origin_dir):
	lordict = {'RIGHT':'R', 'LEFT':'L'}
	typedict = {}
	info = np.loadtxt(txt_dir, str, skiprows=1, usecols=(3, 8, 9, 10))
	pids = info[0]
	lors = info[1]
	lors = [lordict[i] for i in lors]
	dirs = info[2]
	types = info[3]
	for i in range(len(info)):
		tar_dir = dirs[i]
		out_dir = origin_dir + typedict[types[i]]
		lor = lors[i]
		pid = pids[i]
		tarfile_read(tar_dir, out_dir, pid, lor, wave)

def type_search(txt_dir):
	types = np.loadtxt(txt_dir, str, delimiter='\t', skiprows=1, usecols=-2)
	tmp = np.unique(types)
	tmp = ['_'.join(i.split('_')[:-1]) for i in tmp]
	print(set(tmp))

if __name__ == '__main__':
	txts_dir = '/xdisk/hongxuding/chen/Meta/'
	wave = 'BL'
	origin_dir = '/xdisk/xiaosun/jinchengyu/Slices/'
#	meta_ext(txt_dir, wave, origin_dir)
	txts = ['00_month_files/MR_sub_ex_00month.txt', '18_month_files/MR_sub_ex_18month.txt', '24_month_files/MR_sub_ex_24month.txt',
		 	'30_month_files/MR_sub_ex_30month.txt', '36_month_files/MR_sub_ex_36month.txt', '48_month_files/MR_sub_ex_48month.txt',
			'72_month_files/MR_sub_ex_72month.txt', '96_month_files/MR_sub_ex_96month.txt']
	for txt in txts:
		txt_dir = txts_dir + txt
		type_search(txt_dir)


