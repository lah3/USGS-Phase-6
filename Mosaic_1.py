import arcpy,os
from arcpy import env
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

mos_final_1  = "D:/mos_final_1.gdb"
mos_final_2  = "D:/mos_final_2.gdb"
mos_final_3  = "D:/mos_final_3.gdb"
mos_final_4  = "D:/mos_final_4.gdb"
mos_final_5  = "D:/mos_final_5.gdb"
mos_final_6  = "D:/mos_final_6.gdb"
mos_final_7 = "D:/mos_final_7.gdb"
mos_final_8 = "D:/mos_final_8.gdb"
mos_final_9 = "D:/mos_final_9.gdb"
mos_final_10 = "D:/mos_final_10.gdb"
mos_final_11 = "D:/mos_final_11.gdb"
mos_final_12 = "D:/mos_final_12.gdb"
mos_final_13 = "D:/mos_final_13.gdb"


final_1  = "D:/final_1.gdb"
final_2  = "D:/final_2.gdb"
final_3  = "D:/final_3.gdb"
final_4  = "D:/final_4.gdb"
final_5  = "D:/final_5.gdb"
final_6  = "D:/final_6.gdb"
final_7 = "D:/final_7.gdb"
final_8 = "D:/final_8.gdb"
final_9 = "D:/final_9.gdb"
final_10 = "D:/final_10.gdb"
final_11 = "D:/final_11.gdb"
final_12 = "D:/final_12.gdb"
final_13 = "D:/final_13.gdb"

#Lists 
md_list = [mos_final_1, mos_final_2, mos_final_3, mos_final_4, mos_final_5, mos_final_6, mos_final_7, mos_final_8, mos_final_9, mos_final_10, mos_final_11, mos_final_12, mos_final_13]

final_list = [final_1, final_2, final_3, final_4, final_5, final_6, final_7, final_8, final_9, final_10, final_11, final_12, final_13]

class_list = ['CRP', 'FOREST', 'INR', 'IR', 'MO', 'PAS', 'TCI', 'TCT', 'TG', 'WAT', 'WLF', 'WLO', 'WLT']


# Creates mosaic datasets
for i in md_list:
	if arcpy.Exists(i):
		print i + ": Exists (MD)"
	else:
		gdb_name = os.path.basename(i)
		gdb = os.path.splitext(gdb_name)[0]
		arcpy.CreateFileGDB_management("D:/", gdb )

# Creates output datasets
for i in final_list:
	if arcpy.Exists(i):
		print i + ": Exists (Final)"
	else:
		gdb_name = os.path.basename(i)
		gdb = os.path.splitext(gdb_name)[0]
		arcpy.CreateFileGDB_management("D:/", gdb )

for f, c in zip(md_list, class_list):
	coord = arcpy.SpatialReference(3857)
	arcpy.CreateMosaicDataset_management(f, c, coord, "1","8_BIT_UNSIGNED")

print "---Mosaic Datasets Created---"

#Raster Lists 
CRP_List = []
FOREST_List = []
INR_List = []
IR_List = []
MO_List = []
PAS_List = []
TCI_List = []
TCT_List = []
TG_List = []
WAT_List = []
WLF_List = []
WLO_List = []
WLT_List = []

arcpy.env.workspace = "D:/A__P6_FINAL_TIFFs"

for folder in arcpy.ListWorkspaces("*"):
	folder_basename = os.path.basename(folder)
	CoName = folder_basename.rsplit('_',1)[0]
	env.workspace = os.path.join("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL")

	for raster in arcpy.ListRasters("*_CRP.tif"):
		if arcpy.Exists(raster):
			CRP_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*FOR.tif"):
		if arcpy.Exists(raster):
			FOREST_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*_INR.tif"):
		if arcpy.Exists(raster):
			INR_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*_IR.tif"):
		if arcpy.Exists(raster):
			IR_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*_MO.tif"):
		if arcpy.Exists(raster):
			MO_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*_PAS.tif"):
		if arcpy.Exists(raster):
			PAS_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*_TCI.tif"):
		if arcpy.Exists(raster):
			TCI_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*_TCT.tif"):
		if arcpy.Exists(raster):
			TCT_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*_TG.tif"):
		if arcpy.Exists(raster):
			TG_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*_WAT.tif"):
		if arcpy.Exists(raster):
			WAT_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*_WLF.tif"):
		if arcpy.Exists(raster):
			WLF_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*_WLO.tif"):
		if arcpy.Exists(raster):
			WLO_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

	for raster in arcpy.ListRasters("*_WLT.tif"):
		if arcpy.Exists(raster):
			WLT_List.append("D:/A__P6_FINAL_TIFFs/" + CoName + "_FINAL/" + raster)

print "---Raster lists compiled for Non-VA Counties---"

arcpy.env.workspace = "D:/A__P6_FINAL_TIFFs_VA"

for folder in arcpy.ListWorkspaces("*"):
	CoName = os.path.basename(folder)
	env.workspace = os.path.join("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs")

	for raster in arcpy.ListRasters("*_CRP.tif"):
		if arcpy.Exists(raster):
			CRP_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*FOR.tif"):
		if arcpy.Exists(raster):
			FOREST_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*_INR.tif"):
		if arcpy.Exists(raster):
			INR_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*_IR.tif"):
		if arcpy.Exists(raster):
			IR_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*_MO.tif"):
		if arcpy.Exists(raster):
			MO_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*_PAS.tif"):
		if arcpy.Exists(raster):
			PAS_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*_TCI.tif"):
		if arcpy.Exists(raster):
			TCI_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*_TCT.tif"):
		if arcpy.Exists(raster):
			TCT_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*_TG.tif"):
		if arcpy.Exists(raster):
			TG_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*_WAT.tif"):
		if arcpy.Exists(raster):
			WAT_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*_WLF.tif"):
		if arcpy.Exists(raster):
			WLF_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*_WLO.tif"):
		if arcpy.Exists(raster):
			WLO_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

	for raster in arcpy.ListRasters("*_WLT.tif"):
		if arcpy.Exists(raster):
			WLT_List.append("D:/A__P6_FINAL_TIFFs_VA/" + CoName + "/Final_Tiffs/" + raster)

print "---Raster lists compiled for VA Counties---"

#Add rasters to specific mosaic dataset

input_path = ";".join(CRP_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_1.gdb/CRP", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(FOREST_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_2.gdb/FOREST", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(INR_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_3.gdb/INR", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(IR_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_4.gdb/IR", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(MO_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_5.gdb/MO", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(PAS_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_6.gdb/PAS", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(TCI_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_7.gdb/TCI", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(TCT_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_8.gdb/TCT", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(TG_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_9.gdb/TG", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(WAT_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_10.gdb/WAT", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(WLF_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_11.gdb/WLF", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(WLO_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_12.gdb/WLO", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

input_path = ";".join(WLT_List)
arcpy.AddRastersToMosaicDataset_management("D:/mos_final_13.gdb/WLT", "Raster Dataset", input_path, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "", "", "", "#", "SUBFOLDERS","ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "#", "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", "")

print "---All Rasters Added---"
"""
env.snapRaster =r'G:\ImageryServer\A__Snap\Phase6_Snap.tif'
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)
output_dir = "D:/final.gdb/"

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_1.gdb/CRP", output_dir + "CRP", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- CRP Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_1.gdb/FOREST", output_dir + "FOREST", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- FOREST Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_1.gdb/INR", output_dir + "INR", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- INR Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_2.gdb/IR", output_dir + "IR", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- IR Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_2.gdb/MO", output_dir + "MO", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- MO Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_2.gdb/PAS", output_dir + "PAS", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- PAS Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_3.gdb/TCI", output_dir + "TCI", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- TCI Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_3.gdb/TCT", output_dir + "TCT", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- TCT Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_3.gdb/TG", output_dir + "TG", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- TG Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_4.gdb/WAT", output_dir + "WAT", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- WAT Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_4.gdb/WLF", output_dir + "WLF", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- WLF Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_4.gdb/WLO", output_dir + "WLO", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- WLO Complete %s seconds ---" % (time.time() - start_time))

start_time = time.time()
arcpy.CopyRaster_management("D:/mos_final_4.gdb/WLT", output_dir + "WLT", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
print("--- WLT Complete %s seconds ---" % (time.time() - start_time))

arcpy.CopyRaster_management("D:/mos_final.gdb/CRP", output_dir + "CRP", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
arcpy.CopyRaster_management("D:/mos_final.gdb/FOREST", output_dir + "FOREST", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
arcpy.CopyRaster_management("D:/mos_final.gdb/INR", output_dir + "INR", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
arcpy.CopyRaster_management("D:/mos_final.gdb/IR", output_dir + "IR", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
arcpy.CopyRaster_management("D:/mos_final.gdb/MO", output_dir + "MO", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
arcpy.CopyRaster_management("D:/mos_final.gdb/PAS", output_dir + "PAS", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
arcpy.CopyRaster_management("D:/mos_final.gdb/TCI", output_dir + "TCI", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
arcpy.CopyRaster_management("D:/mos_final.gdb/TCT", output_dir + "TCT", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")

arcpy.CopyRaster_management("D:/mos_final_3.gdb/TG", output_dir + "TG", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")

arcpy.CopyRaster_management("D:/mos_final.gdb/WAT", output_dir + "WAT", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
arcpy.CopyRaster_management("D:/mos_final.gdb/WLF", output_dir + "WLF", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
arcpy.CopyRaster_management("D:/mos_final.gdb/WLO", output_dir + "WLO", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
arcpy.CopyRaster_management("D:/mos_final.gdb/WLT", output_dir + "WLT", "", "", "", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "", "NONE")
"""