
import os
import unittest

import numpy as np
# import vtk
# from ccpi.viewer.utils.conversion import (Converter, cilRawResampleReader, cilMetaImageResampleReader,
#                                           cilNumpyResampleReader, cilNumpyMETAImageWriter,
#                                           vortexTIFFResampleReader)
# import warnings

from ccpi.viewer.utils.conversion import cilNumpyMETAImageWriter
from ccpi.viewer.utils.conversion import Converter

bits = 8
shape = (5, 4, 6)
size = shape[0] * shape[1] * shape[2]
# input_3D_array = np.reshape(np.arange(size), newshape=shape)\
#     .astype(dtype=eval(f"np.uint{bits}"))

input_3D_array = np.zeros(shape).astype(dtype=np.uint8)
print(input_3D_array.shape)

# each slice has the same value i
for k in range(shape[2]):
    for j in range(shape[1]):
        for i in range(shape[0]):
            input_3D_array[i, j, k] = i


idx = 0
num_slices = 2
print (input_3D_array[idx:idx+num_slices])

# Write File to disk with numpy
raw_fname = 'raw_test_file.raw'
input_3D_array.tofile(raw_fname)


data_filename = raw_fname
header_filename = 'raw_header.mhd'
typecode = 'uint8'
big_endian = False
header_length = 0

def save_mhd(data_filename, header_filename, input_3D_array, typecode, big_endian, header_length=0):
    shape = np.shape(input_3D_array)
    shape_to_write = shape
    if input_3D_array.flags['C_CONTIGUOUS']:
        shape_to_write = shape[::-1]
    cilNumpyMETAImageWriter.WriteMETAImageHeader(data_filename,
                                                    header_filename,
                                                    typecode,
                                                    big_endian,
                                                    header_length,
                                                    shape_to_write,
                                                    spacing=(1., 1., 1.),
                                                    origin=(0., 0., 0.))

save_mhd(data_filename, header_filename, input_3D_array, typecode, big_endian, header_length)

# from ccpi.viewer.utils.conversion import cilRawCroppedReader

# reader = cilRawCroppedReader()
# reader.SetFileName(raw_fname)
# reader.SetTargetZExtent((idx, idx+num_slices))
# reader.SetBigEndian(False)
# reader.SetIsFortran(False)
# reader.SetTypeCodeName("uint8")
# reader.SetStoredArrayShape(shape)
# reader.Update()
# image = reader.GetOutput()


is_fortran = False
shape_to_write = input_3D_array.shape
if input_3D_array.flags['F_CONTIGUOUS']:
    is_fortran = True
    shape_to_write = input_3D_array.shape[::-1]

from ccpi.viewer.utils.conversion import cilMetaImageCroppedReader
reader = cilMetaImageCroppedReader()
reader.SetFileName(header_filename)
reader.SetTargetZExtent((idx, idx+num_slices))
reader.SetBigEndian(False)
reader.SetIsFortran(is_fortran)
reader.SetTypeCodeName(typecode)
reader.SetStoredArrayShape(shape_to_write)
reader.Update()

image = reader.GetOutput()

print(f"image.GetDimensions() {image.GetDimensions()}")
from ccpi.viewer.utils.conversion import Converter

img_back = Converter.vtk2numpy(image)

print(f"img_back.shape {img_back.shape}")
print (f"extent {image.GetExtent()}, expected {(idx, idx+num_slices, 0, shape[1]-1, 0, shape[2]-1)}")
try:
    print(img_back)
except Exception as err:
    print(f"{err}")

##### Fortran
if True:
    print ("############## TESTING FORTRAN ORDER ##################")
    input_3D_array = np.zeros(shape).astype(dtype=np.uint8)
    input_3D_array = np.asfortranarray(input_3D_array)
    print(input_3D_array.shape)
    shape = input_3D_array.shape[:]

    # each slice has the same value i
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                input_3D_array[i, j, k] = i


    # idx = 1
    print (input_3D_array[idx:idx+num_slices])

    # Write File to disk with numpy
    raw_fname = 'raw_test_file_fortran.raw'
    input_3D_array.tofile(raw_fname)


    is_fortran = False
    shape_to_write = input_3D_array.shape
    if input_3D_array.flags['F_CONTIGUOUS']:
        print ("It is fortran")
        is_fortran = True
        shape_to_write = input_3D_array.shape[::-1]

    save_mhd(raw_fname, header_filename, input_3D_array, typecode, big_endian, header_length)


    from ccpi.viewer.utils.conversion import cilMetaImageCroppedReader
    reader = cilMetaImageCroppedReader()
    reader.SetFileName(header_filename)
    reader.SetTargetZExtent((idx, idx+num_slices))
    reader.SetBigEndian(False)
    reader.SetIsFortran(is_fortran)
    reader.SetTypeCodeName(typecode)
    reader.SetStoredArrayShape(shape_to_write)
    reader.Update()
    image = reader.GetOutput()

    print(f"image.GetDimensions() {image.GetDimensions()}")
    from ccpi.viewer.utils.conversion import Converter

    img_back = Converter.vtk2numpy(image, 'C')

    read_back = np.fromfile(raw_fname, dtype=typecode)
    print(f">>>>>>>>>>>>>>>>>>> {read_back.size}")

    for i in range(img_back.size):
        print (f"img_back {img_back.ravel()[i]} read_back {read_back[i]}")

    read_back.shape = input_3D_array.shape
    print(">>>>>>>>> shapes ", read_back.shape, img_back.shape)
    print(">>>>>>>>> img_back ", img_back)
    print(">>>>>>>>> read_back ", read_back[idx:idx+num_slices+1])
    print(f">>>>>>>>> read_back flags {read_back.flags}")
    np.testing.assert_array_equal(img_back, read_back[idx:idx+num_slices+1])
    print(f"img_back.shape {img_back.shape}")

    print (f"extent {image.GetExtent()}, expected {(0, shape[2]-1, 0, shape[1]-1, idx, idx+num_slices)}")

    try:
        print(img_back)
    except Exception as err:
        print(f"{err}")