import vtk
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk import vtkPolyData, vtkAlgorithmOutput, vtkImageData

from numbers import Integral, Number

class cilClipPolyDataBetweenPlanes(VTKPythonAlgorithmBase):
    '''A vtkAlgorithm to clip a polydata between two planes
    
    It is meant to be used by the CILViewer2D to clip the polydata it's 
    displaying to the current slice.
    
    It works based on the definition of 2 vtkPlane and 2 vtkClipPolyData 
    whose clip function are the mentioned planes. 
    
    Input: polydata
           origin and normal of Plane Above displayed slice
           origin and normal of Plane Below displayed slice
    '''
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=1, nOutputPorts=1)
        self.__PlaneOriginAbove    = None
        self.__PlaneNormalAbove    = None
        self.__PlaneOriginBelow    = None
        self.__PlaneNormalBelow    = None
        
        # self.planesource = [ vtk.vtkPlaneSource(), vtk.vtkPlaneSource() ]
        self.visPlane = [ vtk.vtkPlane() , vtk.vtkPlane() ]
        self.planeClipper =  [ vtk.vtkClipPolyData() , vtk.vtkClipPolyData()]
        self.planeClipper[1].SetInputConnection(self.planeClipper[0].GetOutputPort())
        
                
        self.planeClipper[0].SetClipFunction(self.visPlane[0])
        self.planeClipper[1].SetClipFunction(self.visPlane[1])
        
        self.planeClipper[0].InsideOutOn()
        self.planeClipper[1].InsideOutOn()
            

    def SetPlaneOriginAbove(self, value):
        if not (isinstance(value, list) or isinstance(value, tuple)):
            raise ValueError('Spacing should be a list or a tuple. Got', type(value))
        if value != self.__PlaneOriginAbove:
            # print ("SetPlaneOriginAbove", value)
            self.__PlaneOriginAbove = value
            self.Modified()
    def GetPlaneOriginAbove(self):
        return self.__PlaneOriginAbove
    def SetPlaneNormalAbove(self, value):
        if not (isinstance(value, list) or isinstance(value, tuple)):
            raise ValueError('Spacing should be a list or a tuple. Got', type(value))
        if value != self.__PlaneNormalAbove:
            self.__PlaneNormalAbove = value
            self.Modified()
    def GetPlaneNormalAbove(self):
        return self.__PlaneNormalAbove
    def SetPlaneOriginBelow(self, value):
        if not (isinstance(value, list) or isinstance(value, tuple)):
            raise ValueError('Spacing should be a list or a tuple. Got', type(value))
        if value != self.__PlaneOriginBelow:
            # print ("SetPlaneOriginBelow", value)
            self.__PlaneOriginBelow = value
            self.Modified()
    def GetPlaneOriginBelow(self):
        return self.__PlaneOriginBelow
    def SetPlaneNormalBelow(self, value):
        if not (isinstance(value, list) or isinstance(value, tuple)):
            raise ValueError('Spacing should be a list or a tuple. Got', type(value))
        if value != self.__PlaneNormalBelow:
            self.__PlaneNormalBelow = value
            self.Modified()
    def GetPlaneNormalBelow(self):
        return self.__PlaneNormalBelow

    def FillInputPortInformation(self, port, info):
        if port == 0:
            info.Set(vtk.vtkAlgorithm.INPUT_REQUIRED_DATA_TYPE(), "vtkPolyData")
        return 1

    def FillOutputPortInformation(self, port, info):
        info.Set(vtk.vtkDataObject.DATA_TYPE_NAME(), "vtkPolyData")
        return 1

    def RequestData(self, request, inInfo, outInfo):
        try:
            print("Request Data")
            inp = vtk.vtkPolyData.GetData(inInfo[0])
            out = vtk.vtkPolyData.GetData(outInfo)
            # print ("input number of points" , inp.GetPoints().GetNumberOfPoints())

            self.planeClipper[0].SetInputData(inp)
            # self.planeClipper[1].SetInputConnection(self.planeClipper[0].GetOutputPort())

            # print("Above Plane {} {}".format(self.GetPlaneOriginAbove(), self.GetPlaneNormalAbove()))

            self.visPlane[0].SetOrigin(*self.GetPlaneOriginAbove())
            self.visPlane[0].SetNormal(*self.GetPlaneNormalAbove())

            # print("Below Plane {} {}".format(self.GetPlaneOriginBelow(), self.GetPlaneNormalBelow()))

            self.visPlane[1].SetOrigin(*self.GetPlaneOriginBelow())
            self.visPlane[1].SetNormal(*self.GetPlaneNormalBelow())

            # self.planesource[0].SetCenter(self.visPlane[0].GetOrigin())
            # self.planesource[0].SetNormal(self.visPlane[0].GetNormal())

            # self.planesource[1].SetCenter(self.visPlane[1].GetOrigin())
            # self.planesource[1].SetNormal(self.visPlane[1].GetNormal())

            self.planeClipper[0].Update()
            # print ("planeclipper0 number of points" , self.planeClipper[0].GetOutput().GetPoints().GetNumberOfPoints())

            self.planeClipper[1].Update()
            # print ("planeclipper1 number of points" , self.planeClipper[1].GetOutput().GetPoints().GetNumberOfPoints())


            # put the output in the out port
            # out.ShallowCopy(self.planeClipper[0].GetOutput())
            out.ShallowCopy(self.planeClipper[1].GetOutput())
            return 1

        except Exception as e:
             print (e)
             print ("Plane origin/s and/or normal/s not set.")


class cilPlaneClipper(object):


    def __init__(self, interactor, data_list_to_clip = {}):
        self.SetInteractor(interactor)
        self.SetDataListToClip(data_list_to_clip)

    def SetDataListToClip(self, data_list_to_clip):
        self.DataListToClip = {}
        for key, data_to_clip in data_list_to_clip:
             self.AddDataToClip(key, data_to_clip)

    def AddDataToClip(self, key, data_to_clip):
        self.DataListToClip[str(key)] = self.MakeClippableData(data_to_clip)
        self.UpdateClippingPlanes()

    def RemoveDataToClip(self, key):
        if key in self.DataListToClip.keys():
            self.DataListToClip.pop(key)

    def MakeClippableData(self, data_to_clip):
        clippable_data = cilClipPolyDataBetweenPlanes()
        if isinstance(data_to_clip, vtkPolyData):
            #print("Polydata")
            clippable_data.SetInputDataObject(data_to_clip)
        elif isinstance(data_to_clip, vtkAlgorithmOutput):
            #print("Algorithm Output")
            clippable_data.SetInputConnection(data_to_clip)
        else:
            print("Data To Clip must be vtkPolyData or vtkAlgorithmOutput")
            return None
        return clippable_data

    def GetDataListToClip(self):
        return self.DataListToClip

    def GetClippedData(self, key):
        return self.DataListToClip[key]
    
    def SetInteractor(self, interactor):
         self.Interactor = interactor

    def GetInteractor(self):
         return self.Interactor

    def UpdateClippingPlanes(self, interactor = None, event = "ClipData"):
        try:
            if len(self.DataListToClip) > 0:
                if interactor is None:
                    interactor = self.Interactor
                print("Update Clipping Planes", self.DataListToClip)
                
                print("Orientation", interactor.GetSliceOrientation())
                #print("Interactor", interactor)
                normal = [0, 0, 0]
                origin = [0, 0, 0]
                norm = 1

                orientation = interactor.GetSliceOrientation()

                print("Current active slice", interactor.GetActiveSlice())

                spac = interactor.GetInputData().GetSpacing()
                orig = interactor.GetInputData().GetOrigin()
                slice_thickness = spac[orientation]

                beta_up = 0.5 - 1e-9
                beta_down = 0.5
   
                normal[orientation] = norm
                origin [orientation] = (interactor.GetActiveSlice()) * slice_thickness + beta_up #- orig[orientation]

                # update the  plane below
                slice_below = interactor.GetActiveSlice() 

                origin_below = [i for i in origin]
                origin_below[orientation] = ( slice_below ) * slice_thickness - beta_down #- orig[orientation]

                for data_to_clip in self.DataListToClip.values():
                    data_to_clip.SetPlaneOriginAbove(origin)
                    data_to_clip.SetPlaneNormalAbove(normal)
                    data_to_clip.SetPlaneOriginBelow(origin_below)
                    data_to_clip.SetPlaneNormalBelow((-normal[0], -normal[1], -normal[2]))
                    data_to_clip.Update()
                
                interactor.UpdatePipeline()

                
        except AttributeError as ae:
            print (ae)
            print ("No data to clip.")


class cilMaskPolyData(VTKPythonAlgorithmBase):
    '''vtkAlgorithm to crop a vtkPolyData with a Mask

    This is really only meant for point clouds: see points2vertices function
    '''
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self, nInputPorts=2, nOutputPorts=1)
        self.__MaskValue = 1

    def SetMaskValue(self, mask_value):
        '''Sets the value at which the mask is active'''
        if not isinstance(mask_value, Integral):
            raise ValueError('Mask value must be an integer. Got' , mask_value)

        if mask_value != self.__MaskValue:
            self.__MaskValue = mask_value
            self.Modified()

    def GetMaskValue(self):
        return self.__MaskValue

    def FillInputPortInformation(self, port, info):
        if port == 0:
            info.Set(vtk.vtkAlgorithm.INPUT_REQUIRED_DATA_TYPE(), "vtkPolyData")
        elif port == 1:
            info.Set(vtk.vtkAlgorithm.INPUT_REQUIRED_DATA_TYPE(), "vtkImageData")
        return 1

    def FillOutputPortInformation(self, port, info):
        info.Set(vtk.vtkDataObject.DATA_TYPE_NAME(), "vtkPolyData")
        return 1

    def RequestData(self, request, inInfo, outInfo):
        self.point_in_mask = 0
        in_points = vtk.vtkDataSet.GetData(inInfo[0])
        mask = vtk.vtkDataSet.GetData(inInfo[1])
        out_points = vtk.vtkPoints()
        
        # this implementation is slightly more efficient
        spac = mask.GetSpacing()
        orig = mask.GetOrigin()
        for i in range(in_points.GetNumberOfPoints()):
            pp = in_points.GetPoint(i)

            # get the point in image coordinate

            # ic = self.world2imageCoordinate(pp, mask)
            ic = [int(pp[i] / spac[i] + orig[i]) for i in range(3)]
            i = 0
            outside = False
            while i < len(ic):
                outside = ic[i] < 0 or ic[i] >= mask.GetDimensions()[i]
                if outside:
                    break
                i += 1

            if not outside:
                mm = mask.GetScalarComponentAsDouble(int(ic[0]),
                                                      int(ic[1]),
                                                      int(ic[2]), 0)

                if int(mm) == int(self.GetMaskValue()):
                    # print ("value of point {} {}".format(mm, ic))
                    out_points.InsertNextPoint(*pp)
                    self.point_in_mask += 1

        vertices = self.points2vertices(out_points)
        pointPolyData = vtk.vtkPolyData.GetData(outInfo)
        pointPolyData.SetPoints(out_points)
        pointPolyData.SetVerts(vertices)
        print ("points in mask", self.point_in_mask)
        return 1

    def world2imageCoordinate(self, world_coordinates, imagedata):
        """
        Convert from the world or global coordinates to image coordinates
        :param world_coordinates: (x,y,z)
        :return: rounded to next integer (x,y,z) in image coorindates eg. slice index
        """
        # dims = imagedata.GetDimensions()
        spac = imagedata.GetSpacing()
        orig = imagedata.GetOrigin()

        return [round(world_coordinates[i] / spac[i] + orig[i]) for i in range(3)]
    def points2vertices(self, points):
        '''returns a vtkCellArray from a vtkPoints'''

        vertices = vtk.vtkCellArray()
        for i in range(points.GetNumberOfPoints()):
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(i)
            # print (points.GetPoint(i))
        return vertices