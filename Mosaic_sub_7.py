import arcpy,os,time
from arcpy import env
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

env.snapRaster =r'G:\ImageryServer\A__Snap\Phase6_Snap.tif'
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)
output_dir = "D:/final_7.gdb/"

print "---Copying Rasters Started---"

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_7.gdb/TCI", output_dir + "TCI", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- TCI Complete %s seconds ---" % (time.time() - start_time))