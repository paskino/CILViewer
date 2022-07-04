import os, site

dirname = os.path.abspath('C:/Users/ofn77899/Dev/CILViewer/src/buildpy/INSTALL/bin/Lib/site-packages')
site.addsitedir(dirname)
os.add_dll_directory(os.path.join(dirname, 'wrapping'))

from wrapping import vtkWrappable

wrap = vtkWrappable.vtkWrapped()
assert wrap.GetString() == 'wrapped'
