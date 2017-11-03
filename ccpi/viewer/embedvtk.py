# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 12:18:58 2017

@author: ofn77899
"""

#!/usr/bin/env python
 
import sys
import vtk
from PyQt5 import QtCore, QtWidgets
from ccpi.viewer.QVTKCILViewer import QVTKCILViewer
from ccpi.viewer.CILViewer2D import CILViewer2D , Converter, CILInteractorStyle
import numpy
 
class MainWindow(QtWidgets.QMainWindow):
 
    def __init__(self, parent = None):
        QtWidgets.QMainWindow.__init__(self, parent)
 
        self.frame = QtWidgets.QFrame()
 
        self.vl = QtWidgets.QVBoxLayout()
        self.vtkWidget = QVTKCILViewer(self.frame)
        self.iren = self.vtkWidget.GetInteractor()
        self.vl.addWidget(self.vtkWidget)
        
        
   
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)
        

    def displayExample(self):
        # Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(0, 0, 0)
        source.SetRadius(5.0)
   
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        self.ren = self.vtkWidget.GetRenderer()
        
        self.ren.AddActor(actor)
        self.show()
        self.iren.Initialize()

    def display(self, imageData):
        if type(imageData) == vtk.vtkCommonDataModelPython.vtkImageData:
            self.vtkWidget.setInput3DData(imageData)
        elif type(imageData) == numpy.ndarray:
            self.vtkWidget.setInputAsNumpy(imageData)
        self.iren.Initialize()
        self.show()

 
if __name__ == "__main__":
 
    app = QtWidgets.QApplication(sys.argv)
 
    window = MainWindow()
##    reader = vtk.vtkMetaImageReader()
##    reader.SetFileName("C:\\Users\\ofn77899\\Documents\\GitHub\\CCPi-Simpleflex\\data\\head.mha")
##    reader.Update()
    
##    window.display(reader.GetOutput())
 
    X = numpy.load("C:\\Users\\ofn77899\\Documents\\GitHub\\CCPi-FISTA_reconstruction\\src\\Python\\test\\FISTA.npy")
    window.display(X)  
    sys.exit(app.exec_())