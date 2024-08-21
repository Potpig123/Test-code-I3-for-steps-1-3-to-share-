import numpy as np
import pydicom
import os
import tarfile
from io import BytesIO
import zlib

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
		except zlib.error as e:
			print(f"Error reading tar members: {e}")
			return
		
		for member in members:
			if member.isfile():
				file = tars.extractfile(member)
				if file is None:
					continue

				name = member.name[2:]
				name = pid + lor + wave + name + type + '.npy'
				save_dir = os.path.join(out_dir,name)
				
				content = file.read()
				if readable_dicom_file(content):
					img = pydicom.dcmread(BytesIO(content)).pixel_array
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
	lordict = {'RIGHT':'R', 'LEFT':'L'}
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

if __name__ == '__main__':
	txts_dir = '/xdisk/hongxuding/chen/Meta/18_month_files/MR_sub_ex_18month.txt'
	wave = 'M18'
	origin_dir = '/xdisk/xiaosun/jinchengyu/M18T/'

#	txts = ['00_month_files/MR_sub_ex_00month.txt', '18_month_files/MR_sub_ex_18month.txt', '24_month_files/MR_sub_ex_24month.txt',
#		 	'30_month_files/MR_sub_ex_30month.txt', '36_month_files/MR_sub_ex_36month.txt', '48_month_files/MR_sub_ex_48month.txt',
#			'72_month_files/MR_sub_ex_72month.txt', '96_month_files/MR_sub_ex_96month.txt']

	meta_ext(txts_dir, wave, origin_dir)

#	out_dir = '/xdisk/hongxuding/jinchengyu/pngs/'
#	tars_dir = ['/xdisk/xiaosun/jinchengyu/OAI/Package_1230090/image03/18m/2.D.2/9488441/20051228/10643608.tar.gz',
#				'/xdisk/xiaosun/jinchengyu/OAI/Package_1230090/image03/18m/2.D.2/9556464/20051229/10642908.tar.gz',
#			 	'/xdisk/xiaosun/jinchengyu/OAI/Package_1230090/image03/18m/2.D.2/9436426/20051222/10644208.tar.gz']
#	for tar_dir in tars_dir:
#		tarfile_read(tar_dir,out_dir, type='TEST',pid='123321',lor='R', wave='M18')
