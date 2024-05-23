
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


idx = 1
num_slices = 2
print (input_3D_array[idx:idx+num_slices])

rawfname = 'raw_test_file.raw'
# Write File to disk with numpy
input_3D_array.tofile(rawfname)

data_filename = rawfname
header_filename = 'raw_header.mhd'
typecode = 'uint8'
big_endian = False
header_length = 0
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

import vtk
reader = vtk.vtkMetaImageReader()
reader.SetFileName(header_filename)
reader.Update()

print(f"reader.GetOutput().GetDimensions() {reader.GetOutput().GetDimensions()}")

# for k in range(shape[2]):
#     for j in range(shape[1]):
#         for i in range(shape[0]):
#             print ( input_3D_array[i, j, k], 
#                     int( reader.GetOutput().GetScalarComponentAsDouble(k, j, i, 0) )
#                    )

arr = Converter.vtk2numpy(reader.GetOutput(), order='C')

np.testing.assert_array_equal(input_3D_array, arr)


# from ccpi.viewer.utils.conversion import cilRawCroppedReader

# reader = cilRawCroppedReader()
# reader.SetFileName('numpy_raw_test_file.raw')
# reader.SetTargetZExtent((idx, idx+num_slices))
# reader.SetBigEndian(False)
# reader.SetIsFortran(False)
# reader.SetTypeCodeName("uint8")
# reader.SetStoredArrayShape(shape)
# reader.Update()
# image = reader.GetOutput()

# print(f"image.GetDimensions() {image.GetDimensions()}")
# from ccpi.viewer.utils.conversion import Converter

# img_back = Converter.vtk2numpy(image)

# print(f"img_back.shape {img_back.shape}")
# print (f"extent {image.GetExtent()}, expected {(idx, idx+num_slices, 0, shape[1]-1, 0, shape[2]-1)}")
# try:
#     print(img_back)
# except Exception as err:
#     print(f"{err}")

##### Fortran
print ("############## TESTING FORTRAN ORDER ##################")
# input_3D_array = np.zeros(shape).astype(dtype=np.uint8)
input_3D_array = np.asfortranarray(input_3D_array)

# Write File to disk with numpy
fortran_rawfname = 'numpy_raw_test_file_fortran.raw'
input_3D_array.tofile(fortran_rawfname)

print(input_3D_array.shape)
shape = input_3D_array.shape[:]

# each slice has the same value i
for i in range(shape[0]):
    for j in range(shape[1]):
        for k in range(shape[2]):
            input_3D_array[i, j, k] = i

shape_to_write = shape
if input_3D_array.flags['C_CONTIGUOUS']:
    shape_to_write = shape[::-1]

header_filename = "edo_sucks.mhd"
cilNumpyMETAImageWriter.WriteMETAImageHeader(fortran_rawfname,
                                                header_filename,
                                                typecode,
                                                big_endian,
                                                header_length,
                                                shape_to_write,
                                                spacing=(1., 1., 1.),
                                                origin=(0., 0., 0.))
# reader = vtk.vtkMetaImageReader()
reader.SetFileName(header_filename)
reader.Update()

idx = 1
# print (input_3D_array[idx:idx+num_slices])

read_back = np.fromfile(fortran_rawfname, dtype=np.uint8)

arr = Converter.vtk2numpy(reader.GetOutput(), order='C' if input_3D_array.flags['C_CONTIGUOUS'] else 'F')

print (read_back.shape, arr.shape)
for i in range (read_back.size):
    print (f"{read_back.ravel()[i]}, {arr.ravel()[i]}")
np.testing.assert_array_equal(input_3D_array, arr)

print ("############## TESTING cilMetaImageCroppedReader ##################")

is_fortran = True
writtenshape = shape[::-1]
if input_3D_array.flags['C_CONTIGUOUS']:
    is_fortran = False
    writtenshape = shape[::-1]

from ccpi.viewer.utils.conversion import cilMetaImageCroppedReader
reader = cilMetaImageCroppedReader()
reader.SetFileName(header_filename)
reader.SetTargetZExtent((idx, idx+num_slices))
reader.SetBigEndian(False)
reader.SetIsFortran(is_fortran)
reader.SetTypeCodeName(typecode)
reader.SetStoredArrayShape(writtenshape)
reader.Update()
image = reader.GetOutput()

print(f"image.GetDimensions() {image.GetDimensions()}")
# from ccpi.viewer.utils.conversion import Converter

# img_back = Converter.vtk2numpy(image, 'C')

# print(f"img_back.shape {img_back.shape}")

print (f"extent {image.GetExtent()}, expected {(0, shape[2]-1, 0, shape[1]-1, idx, idx+num_slices)}")
for k in range(idx, idx+num_slices):
    for j in range(shape[1]):
        for i in range(shape[0]):
            print ( #input_3D_array[i, j, k], 
                    int( reader.GetOutput().GetScalarComponentAsDouble(i, j, k, 0) )
                   )
read_back.shape = shape
print(read_back[1])
arr = Converter.vtk2numpy(reader.GetOutput(), order='C')
print(arr[0])

# try:
#     print(img_back)
# except Exception as err:
#     print(f"{err}")