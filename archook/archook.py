'''
Locate ArcPy and add it to the path
Created on 13 Feb 2015
@author: Jamesramm
'''
try:
  import _winreg
except ImportError:
   import winreg as _winreg
import os
import sys

def locate_arcgis(pro=False):
  '''
  Find the path to the ArcGIS Desktop installation, or the ArcGIS Pro installation
  if `pro` argument is True.

  Keys to check:

  ArcGIS Pro: HKLM/SOFTWARE/ESRI/ArcGISPro 'InstallDir'

  HLKM/SOFTWARE/ESRI/ArcGIS 'RealVersion' - will give the version, then we can use
  that to go to
  HKLM/SOFTWARE/ESRI/DesktopXX.X 'InstallDir'. Where XX.X is the version

  We may need to check HKLM/SOFTWARE/Wow6432Node/ESRI instead
  '''
  try:
    if pro:
      pro_key = _winreg.OpenKey(
        _winreg.HKEY_LOCAL_MACHINE,
        'SOFTWARE\\ESRI\\ArcGISPro'
      )
      install_dir = _winreg.QueryValueEx(pro_key, "InstallDir")[0]
    else:
      key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                            'SOFTWARE\\Wow6432Node\\ESRI\\ArcGIS', 0)

      version = _winreg.QueryValueEx(key, "RealVersion")[0][:4]

      key_string = "SOFTWARE\\Wow6432Node\\ESRI\\Desktop{0}".format(version)
      desktop_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                                    key_string, 0)

      install_dir = _winreg.QueryValueEx(desktop_key, "InstallDir")[0]
    return install_dir
  except WindowsError:
    raise ImportError("Could not locate the ArcGIS directory on this machine")

def get_arcpy(pro=False):  
  '''
  Allows arcpy to imported on 'unmanaged' python installations (i.e. python installations
  arcgis is not aware of).
  Gets the location of arcpy and related libs and adds it to sys.path
  Looks for ArcGIS Pro if `pro` argument is True.
  '''
  install_dir = locate_arcgis(pro)
  if pro:
    os.environ['PATH'] = ';'.join((os.path.join(install_dir, 'bin'), os.environ['PATH']))
    sys.path.append(os.path.join(install_dir, 'bin'))
    sys.path.append(os.path.join(install_dir, r'Resources\ArcPy'))
    sys.path.append(os.path.join(install_dir, r'Resources\ArcToolbox\Scripts'))
    sys.path.append(os.path.join(install_dir, r'bin\Python\envs\arcgispro-py3\Lib\site-packages'))
  else:
    arcpy = os.path.join(install_dir, "arcpy")
    # Check we have the arcpy directory.
    if not os.path.exists(arcpy):
      raise ImportError("Could not find arcpy directory in {0}".format(install_dir))

    # First check if we have a bin64 directory - this exists when arcgis is 64bit
    bin_dir = os.path.join(install_dir, "bin64")
    
    # check if we are using a 64-bit version of Python
    is_64bits = sys.maxsize > 2**32
    
    if not os.path.exists(bin_dir) or is_64bits == False:
      # Fall back to regular 'bin' dir otherwise.
      bin_dir = os.path.join(install_dir, "bin")

    scripts = os.path.join(install_dir, "ArcToolbox", "Scripts")  
    sys.path.extend([arcpy, bin_dir, scripts])
