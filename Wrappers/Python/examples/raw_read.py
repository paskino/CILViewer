
import os
import unittest

import numpy as np
# import vtk
# from ccpi.viewer.utils.conversion import (Converter, cilRawResampleReader, cilMetaImageResampleReader,
#                                           cilNumpyResampleReader, cilNumpyMETAImageWriter,
#                                           vortexTIFFResampleReader)
# import warnings

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

# Write File to disk with numpy
input_3D_array.tofile('numpy_raw_test_file.raw')

from ccpi.viewer.utils.conversion import cilRawCroppedReader

reader = cilRawCroppedReader()
reader.SetFileName('numpy_raw_test_file.raw')
reader.SetTargetZExtent((idx, idx+num_slices))
reader.SetBigEndian(False)
reader.SetIsFortran(False)
reader.SetTypeCodeName("uint8")
reader.SetStoredArrayShape(shape)
reader.Update()
image = reader.GetOutput()

print(f"image.GetDimensions() {image.GetDimensions()}")
from ccpi.viewer.utils.conversion import Converter

img_back = Converter.vtk2numpy(image)

print(f"img_back.shape {img_back.shape}")
print (f"extent {image.GetExtent()}, expected {(idx, idx+num_slices, 0, shape[1]-1, 0, shape[2]-1)}")

np.testing.assert_array_equal(img_back, input_3D_array[idx:idx+num_slices+1])

try:
    print(img_back)
except Exception as err:
    print(f"{err}")

##### Fortran
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
input_3D_array.tofile('numpy_raw_test_file_fortran.raw')


reader = cilRawCroppedReader()
reader.SetFileName('numpy_raw_test_file_fortran.raw')
reader.SetTargetZExtent((idx, idx+num_slices))
reader.SetBigEndian(False)
reader.SetIsFortran(True)
reader.SetTypeCodeName("uint8")
reader.SetStoredArrayShape(shape)
reader.Update()
image = reader.GetOutput()

print(f"image.GetDimensions() {image.GetDimensions()}")
from ccpi.viewer.utils.conversion import Converter

img_back = Converter.vtk2numpy(image, 'C')

np.testing.assert_array_equal(img_back, input_3D_array[idx:idx+num_slices+1])
print(f"img_back.shape {img_back.shape}")

print (f"extent {image.GetExtent()}, expected {(0, shape[2]-1, 0, shape[1]-1, idx, idx+num_slices)}")

try:
    print(img_back)
except Exception as err:
    print(f"{err}")