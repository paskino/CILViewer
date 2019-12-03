from ccpi.viewer import *
import vtk

reader = vtk.vtkMetaImageReader()
reader.SetFileName('head.mha')
reader.Update()

v = viewer3D()
v.setInputData(reader.GetOutput())
v.startRenderLoop()