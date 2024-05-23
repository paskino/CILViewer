import os
import unittest

import numpy as np
import vtk
from ccpi.viewer.utils.conversion import (Converter, cilRawCroppedReader, cilMetaImageCroppedReader,
                                          cilNumpyCroppedReader, cilTIFFCroppedReader)
from ccpi.viewer.utils.conversion import cilNumpyMETAImageWriter

def save_mhd(data_filename, header_filename, input_3D_array, typecode, big_endian, header_length=0):
    shape = np.shape(input_3D_array)
    cilNumpyMETAImageWriter.WriteMETAImageHeader(data_filename,
                                                    header_filename,
                                                    typecode,
                                                    big_endian,
                                                    header_length,
                                                    shape,
                                                    spacing=(1., 1., 1.),
                                                    origin=(0., 0., 0.))



class TestCroppedReaders(unittest.TestCase):

    def setUp(self):
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
        # Generate random 3D array and write to HDF5:
        # np.random.seed(1)
        # shape = (5, 4, 6)  # was 10 times larger
        # bits = 8
        # self.input_3D_array = np.random.randint(10, size=shape, dtype=eval(f"np.uint{bits}"))
        # self.input_3D_array = np.reshape(np.arange(self.input_3D_array.size),
        #                                  newshape=shape).astype(dtype=eval(f"np.uint{bits}"))
        self.raw_type_code = str(self.input_3D_array.dtype)
        bytes_3D_array = bytes(self.input_3D_array)
        self.raw_filename_3D = 'test_3D_data.raw'
        with open(self.raw_filename_3D, 'wb') as f:
            f.write(bytes_3D_array)

        self.numpy_filename_3D = 'test_3D_data.npy'
        np.save(self.numpy_filename_3D, self.input_3D_array)

        self.meta_filename_3D = 'test_3D_data.mha'
        vtk_image = Converter.numpy2vtkImage(self.input_3D_array)
        writer = vtk.vtkMetaImageWriter()
        writer.SetFileName(self.meta_filename_3D)
        writer.SetInputData(vtk_image)
        writer.SetCompression(False)
        writer.Write()

        # MHD        
        data_filename = self.raw_filename_3D
        header_filename = 'test_3D_data.mhd'
        self.mhd_header = header_filename
        typecode = self.raw_type_code
        big_endian = False
        header_length = 0
        save_mhd(data_filename, header_filename, self.input_3D_array, typecode, big_endian, header_length)


        input_3D_array_f = np.zeros(shape).astype(dtype=typecode)
        input_3D_array_f = np.asfortranarray(input_3D_array_f)
        shape = input_3D_array_f.shape[:]

        # each slice has the same value i
        for i in range(shape[0]):
            for j in range(shape[1]):
                for k in range(shape[2]):
                    input_3D_array[i, j, k] = i
        # Write File to disk with numpy
        self.raw_fname_f = 'raw_test_file_fortran.raw'
        input_3D_array_f.tofile(self.raw_fname_f)
        self.header_filename_f = 'raw_test_file_fortran.mhd'

        save_mhd(self.raw_fname_f, self.header_filename_f, input_3D_array, typecode, big_endian, header_length)


        # Write TIFFs
        fnames = []
        arr = self.input_3D_array
        from PIL import Image
        for i in range(arr.shape[0]):
            fname = 'tiff_test_file_{:03d}.tiff'.format(i)
            fnames.append(os.path.abspath(fname))
            # Using vtk the Y axis gets reversed
            # vtk_image = Converter.numpy2vtkImage(np.expand_dims(arr[i,:,:], axis=0))
            # twriter.SetFileName(fnames[-1])
            # twriter.SetInputData(vtk_image)
            # twriter.Write()
            im = Image.fromarray(arr[i])
            im.save(fnames[-1])

        self.tiff_fnames = fnames

    def tearDown(self):
        files_to_delete = [self.tiff_fnames, self.meta_filename_3D, 
                           self.raw_filename_3D, self.numpy_filename_3D,
                           self.raw_fname_f, self.header_filename_f]
        import os
        for el in files_to_delete:
            if isinstance(el, (list, tuple)):
                for f in el:
                    if os.path.exists(f):
                        os.remove(f)
            else:
                if os.path.exists(el):
                    os.remove(el)

    def check_extent(self, reader, target_z_extent, is_fortran):
        reader.Update()
        image = reader.GetOutput()
        extent = tuple(image.GetExtent())
        og_shape = np.shape(self.input_3D_array)
        idx = target_z_extent[0]
        num_slices = target_z_extent[1] - target_z_extent[0] + 1
        # if is_fortran:
        #     og_extent = (0, og_shape[2]-1, 0, og_shape[1]-1, idx, idx+num_slices-1)
        # else:
        #     og_extent = (idx, idx+num_slices-1, 0, og_shape[1]-1, 0, og_shape[2]-1)
        j = 1
        if is_fortran:
            i = 2
            k = 0
            og_extent = (0, og_shape[i]-1, 0, og_shape[j]-1,
                       target_z_extent[0], 
                       target_z_extent[1])
        else:
            i = 0
            k = 2 
            og_extent = ( target_z_extent[0], 
                       target_z_extent[1], 
                       0, og_shape[j]-1, 0, og_shape[k]-1)
        expected_extent = og_extent
        # expected_extent[4] = target_z_extent[0]
        # expected_extent[5] = target_z_extent[1]
        self.assertEqual(extent, expected_extent)

    def check_values(self, target_z_extent, read_cropped_image, expected_array=None):
        if expected_array is None:
            expected_array = self.input_3D_array
        read_cropped_array = Converter.vtk2numpy(read_cropped_image)
        cropped_array = expected_array[target_z_extent[0]:target_z_extent[1] + 1, :, :]
        np.testing.assert_array_equal(cropped_array, read_cropped_array)

    def test_raw_cropped_reader(self):
        target_z_extent = [1, 3]
        reader = cilRawCroppedReader()
        og_shape = np.shape(self.input_3D_array)
        reader.SetFileName(self.raw_filename_3D)
        reader.SetTargetZExtent(tuple(target_z_extent))
        reader.SetBigEndian(False)
        is_fortran = False
        reader.SetIsFortran(is_fortran)
        raw_type_code = str(self.input_3D_array.dtype)
        reader.SetTypeCodeName(raw_type_code)
        reader.SetStoredArrayShape(og_shape)
        self.check_extent(reader, target_z_extent, is_fortran)
        self.check_values(target_z_extent, reader.GetOutput())
        # Check raw type code was set correctly:
        self.assertEqual(raw_type_code, reader.GetTypeCodeName())

    def _test_cropped_readers(self, reader, label, filename, is_fortran):
        
        with self.subTest(reader=label):
            target_z_extent = (1, 3)
            reader.SetFileName(filename)
            reader.SetTargetZExtent(target_z_extent)
            reader.SetIsFortran(is_fortran)
            if label == 'cilMetaImageCroppedReader':
                reader.SetBigEndian(False)
                reader.SetIsFortran(is_fortran)
                shape = np.shape(self.input_3D_array)
                shape_to_write = shape
                if self.input_3D_array.flags['C_CONTIGUOUS']:
                    shape_to_write = shape[::-1]
                    
                reader.SetTypeCodeName(self.raw_type_code)
                reader.SetStoredArrayShape(shape_to_write)

            self.check_extent(reader, target_z_extent, is_fortran)
            self.check_values(target_z_extent, reader.GetOutput())
    
    def test_numpy_cropped_reader(self):
        is_fortran = False
        return self._test_cropped_readers(cilNumpyCroppedReader(), 
                                     'cilNumpyCroppedReader',
                                     self.numpy_filename_3D,
                                     is_fortran)
    def test_meta_cropped_reader(self):
        idx=1
        num_slices=2
        
        from ccpi.viewer.utils.conversion import cilMetaImageCroppedReader
        reader = cilMetaImageCroppedReader()
        reader.SetFileName(self.mhd_header)
        reader.SetTargetZExtent((idx, idx+num_slices))
        # reader.SetIsFortran(False)
        reader.Update()

        image = reader.GetOutput()

        print(f"image.GetDimensions() {image.GetDimensions()}")
        from ccpi.viewer.utils.conversion import Converter

        img_back = Converter.vtk2numpy(image, 'F')

        # print(f"img_back.shape {img_back.shape} \ninput_3D_array {input_3D_array[idx:idx+num_slices+1]}")
        # print (f"IMG_BACK >>>>>>>>>>> {img_back}")
        # print (f"INPUT >>>>>>>>>>> {input_3D_array[idx:idx+num_slices+1]}")
        np.testing.assert_array_equal(img_back, self.input_3D_array[idx:idx+num_slices+1])

    def test_meta_cropped_reader_fortran(self):
    
        idx=1
        num_slices=2

        from ccpi.viewer.utils.conversion import cilMetaImageCroppedReader
        reader = cilMetaImageCroppedReader()
        reader.SetFileName(self.header_filename_f)
        reader.SetTargetZExtent((idx, idx+num_slices))
        reader.Update()
        image = reader.GetOutput()

        from ccpi.viewer.utils.conversion import Converter

        img_back = Converter.vtk2numpy(image, 'F')

        read_back = np.fromfile(self.raw_fname_f, dtype=self.raw_type_code)
    
        read_back.shape = self.input_3D_array.shape
        np.testing.assert_array_equal(img_back, read_back[idx:idx+num_slices+1])


    def _setup_tiff_cropped_reader(self, target_z_extent):
        reader = cilTIFFCroppedReader()
        reader.SetFileName(self.tiff_fnames)
        reader.SetTargetZExtent(target_z_extent)
        return reader

    def test_tiff_cropped_reader(self):
        target_z_extent = [1, 3]
        is_fortran = False
        reader = self._setup_tiff_cropped_reader(tuple(target_z_extent))
        self.check_extent(reader, target_z_extent, is_fortran)
        # Check raw type code was set correctly:
        self.assertEqual(self.raw_type_code, reader.GetTypeCodeName())
        self.check_values(target_z_extent, reader.GetOutput())

    def test_tiff_cropped_reader_when_orientation_set(self):
        target_z_extent = [1, 3]
        is_fortran = False
        reader = self._setup_tiff_cropped_reader(tuple(target_z_extent))
        reader.SetOrientationType(4)  # this flips the y axis
        expected_array = np.flip(np.copy(self.input_3D_array), axis=1)
        self.check_extent(reader, target_z_extent, is_fortran)
        # Check raw type code was set correctly:
        self.assertEqual(self.raw_type_code, reader.GetTypeCodeName())
        self.check_values(target_z_extent, reader.GetOutput(), expected_array)

    def tearDown(self):
        files = [self.raw_filename_3D, self.numpy_filename_3D, self.meta_filename_3D] + self.tiff_fnames
        for f in files:
            os.remove(f)


if __name__ == '__main__':
    unittest.main()
