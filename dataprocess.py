import numpy as np
import pydicom
import matplotlib.pyplot as plt
import os


def readable_dicom_file(file):
	try:
		ds = pydicom.dcmread(file)
		expected_length = ds.Rows * ds.Columns * (ds.BitsAllocated // 8)
		if 'PixelData' in ds and len(ds.PixelData) != expected_length:
			return False
		return True
	except pydicom.errors.InvalidDicomError:
		return False


def get_files(file_dir):
	files =  []
	for file in os.listdir(file_dir):
		if file.isdigit():
			files.append(file)
	return files,len(files)		


def npy_file_creation255(filesdir,outfile='example255'):
	files, len_files = get_files(filesdir)
	if len_files >= 36:
		print(filesdir,'has read')
		return
	files.sort()
	npy_data = []
	for file in files:
		file_dir = filesdir + file
		if os.path.getsize(file_dir) < 100000:
			print(file_dir, 'size is not right.')
			continue
		if readable_dicom_file(file_dir):
			data = pydicom.read_file(file_dir).pixel_array
			data -= np.min(data)
			data = (data/np.max(data)*255).astype(np.uint8)
			npy_data.append(data)
		else:
			print(file_dir,'cannot read')
			return
	npy_data = np.array(npy_data)
	outfile = outfile + '.npy'
	np.save(outfile,npy_data)