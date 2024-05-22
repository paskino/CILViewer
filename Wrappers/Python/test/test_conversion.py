import os
import unittest

import numpy as np
import vtk
from ccpi.viewer.utils.conversion import (Converter, cilRawResampleReader, 
                                          cilMetaImageResampleReader,
                                          cilNumpyResampleReader, cilNumpyMETAImageWriter,
                                          cilRawCroppedReader)

import numpy as np
'''
This will test parts of the utils/conversion.py file other than
the Resample and Cropped readers. (See test_cropped_readers.py
and test_resample_readers.py for tests of these)

'''


class TestConversion(unittest.TestCase):

    def setUp(self):
        # Generate random 3D array and write to HDF5:
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

        self.input_3D_array = input_3D_array
        bytes_3D_array = bytes(self.input_3D_array)
        self.raw_filename_3D = 'test_3D_data.raw'
        with open(self.raw_filename_3D, 'wb') as f:
            f.write(bytes_3D_array)

    def tearDown(self):
        files_to_delete = [self.raw_filename_3D]
        import os
        for el in files_to_delete:
            if isinstance(el, (list, tuple)):
                for f in el:
                    if os.path.exists(f):
                        os.remove(f)
            else:
                if os.path.exists(el):
                    os.remove(el)

    def test_WriteMETAImageHeader(self):
        '''writes a mhd file to go with a raw 
        datafile, using cilNumpyMETAImageWriter.WriteMETAImageHeader and then tests if this can
        be read successfully with vtk.vtkMetaImageReader
        by comparing to array read with cilRawResampleReader
        directly from RawResampleReader and the original contents'''

        # read raw file's info:
        data_filename = self.raw_filename_3D
        header_filename = 'raw_header.mhd'
        typecode = 'uint8'
        big_endian = False
        header_length = 0
        shape = np.shape(self.input_3D_array)
        shape_to_write = shape
        if self.input_3D_array.flags['C_CONTIGUOUS']:
            shape_to_write = shape[::-1]
        cilNumpyMETAImageWriter.WriteMETAImageHeader(data_filename,
                                                     header_filename,
                                                     typecode,
                                                     big_endian,
                                                     header_length,
                                                     shape_to_write,
                                                     spacing=(1., 1., 1.),
                                                     origin=(0., 0., 0.))

        reader1 = vtk.vtkMetaImageReader()
        reader1.SetFileName(header_filename)
        reader1.Update()
        
        raw_array = Converter.vtk2numpy(reader1.GetOutput(), 
            order='C' if self.input_3D_array.flags['C_CONTIGUOUS'] else 'F')

        np.testing.assert_array_equal(self.input_3D_array, raw_array)
        
    def tearDown(self):
        files = [self.raw_filename_3D]
        for f in files:
            os.remove(f)


if __name__ == '__main__':
    unittest.main()
