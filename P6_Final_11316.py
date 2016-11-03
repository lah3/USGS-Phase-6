# Final Model P6 LU
#----------------------
import arcpy,os,time,shutil
from arcpy import env 
from arcpy.sa import *

def turf_1(CoName, CoGDB, INR, IR, INRmask, TCI):

	# TURF 1: Mosaic All Non-road Impervious Surfaces
	outCon = Con(Raster(INR)==2,1)
	outCon.save(str(CoName) + "_INRmask")

	if arcpy.Exists(str(CoName) + "_3xImp"):
		print("Impervious Layer Exists")
	else:
		start_time = time.time()
		rasLocation = os.path.join(str(CoGDB))
		inRasters = Raster(IR),Raster(INRmask), Raster(TCI)
		arcpy.MosaicToNewRaster_management(inRasters,rasLocation,str(CoName) + "_3xImp","", "4_BIT", "1", "1", "LAST", "FIRST")
		arcpy.Delete_management("in_memory")
		print("--- TURF #1 Impervious mosaic Complete %s seconds ---" % (time.time() - start_time))

def turf_2(CoName, CoGDB, HERB, BAR, LV):
    # TURF 2: Create Herbaceous Layer
    if arcpy.Exists(str(CoName) + "_Herb"):
        print("Herbaceous Layer Exists")
    else:
        start_time = time.time()
        rasLocation = os.path.join(str(CoGDB))
        inRasters = Raster(BAR),Raster(LV)
        arcpy.MosaicToNewRaster_management(inRasters,rasLocation,str(CoName) + "_Herb","", "4_BIT", "1", "1", "LAST", "FIRST")
        arcpy.Delete_management("in_memory")
        print("--- TURF #2 Herbaceous Mosaic Complete %s seconds ---" % (time.time() - start_time))

def turf_3(CoName, CoGDB, DEV18, DEV27):
    # TURF 3: Identify Potential Rural Turf Based on Proximity to Development
    start_time = time.time()
    arcpy.env.overwriteoutput = True
    outCostDistance = CostDistance(DEV18, DEV27, "10", "", "", "", "", "")
    RTmask = Int(Con(outCostDistance >= 0,1))
    RTmask.save(str(CoName) + "_RTmask")
    arcpy.Delete_management("in_memory")
    print("--- TURF #3 Cost Distance Complete %s seconds ---" % (time.time() - start_time))

def turf_4a(CoName, CoGDB, PARCELS, IR):
    # Step 4a: Repair geometry and check projection and reproject if needed
    start_time = time.time()
    arcpy.RepairGeometry_management(PARCELS, "KEEP_NULL")
    P1 = arcpy.Describe(PARCELS).spatialReference
    P2 = arcpy.Describe(IR).spatialReference
    if arcpy.Exists(str(CoName) + "_ParcelsAlb"):
        PARCELS = os.path.join(str(CoGDB) + str(CoName) + "_ParcelsAlb")
        print("Projected parcel data exists")
    elif P1 == P2:
        arcpy.Rename_management(PARCELS, str(CoName) + "_ParcelsAlb")
        PARCELS = os.path.join(str(CoGDB) + str(CoName) + "_ParcelsAlb")
        print("Parcel projection correct and dataset renamed")
    else:
        arcpy.Project_management(PARCELS, str(CoName) + "_ParcelsAlb", IR)
        PARCELS = os.path.join(str(CoGDB) + str(CoName) + "_ParcelsAlb")
        print("Parcel data reprojected to Albers")
    print("--- TURF #4a Parcel Preprocessing Complete %s seconds ---" % (time.time() - start_time))

def turf_4b(CoName, CoGDB, PARCELS):
    # TURF 4b: Create Turf Parcels
    start_time = time.time()
    arcpy.env.overwriteoutput = True
    arcpy.env.qualifiedFieldNames = "false"
    arcpy.AddField_management(PARCELS, "ACRES2", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(PARCELS, "ACRES2", "!shape.area@acres!", "PYTHON_9.3", "")
    arcpy.AddField_management(PARCELS, "UNIQUEID", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(PARCELS, "UNIQUEID", "!OBJECTID!", "PYTHON_9.3", "")
    arcpy.Select_analysis(PARCELS, str(CoName) + "_Parcels_TURFtemp", 'ACRES2 <= 10')
    Zstat = ZonalStatisticsAsTable(str(CoName) + "_Parcels_TURFtemp", "UNIQUEID", str(CoName) + "_3xImp", "Parcel_IMP", "DATA", "SUM")
    arcpy.JoinField_management(str(CoName) + "_Parcels_TURFtemp", "UNIQUEID", "Parcel_IMP", "UNIQUEID",["SUM"])
    arcpy.Select_analysis(str(CoName) + "_Parcels_TURFtemp", str(CoName) + "_Parcels_TURF", 'SUM >= 93')
    arcpy.AddField_management(str(CoName) + "_Parcels_TURF", "VALUE", "SHORT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(str(CoName) + "_Parcels_TURF", "VALUE", "1", "PYTHON_9.3", "")
    arcpy.FeatureToRaster_conversion(str(CoName) + "_Parcels_TURF", "VALUE", str(CoName) + "_TURF_parcels", 1)
    arcpy.Delete_management("in_memory")
    print("--- TURF #4b Turf Parcels Complete %s seconds ---" % (time.time() - start_time))

def turf_4c(CoName, CoGDB, PARCELS):
    # TURF 4c: Create Fractional Turf Parcels
    start_time = time.time()
    arcpy.Select_analysis(PARCELS, str(CoName) + "_Parcels_FTGtemp", 'ACRES2 > 10')
    Zstat = ZonalStatisticsAsTable(str(CoName) + "_Parcels_FTGtemp", "UNIQUEID", str(CoName) + "_3xImp", "Parcel_IMP2", "DATA", "SUM")
    arcpy.JoinField_management(str(CoName) + "_Parcels_FTGtemp", "UNIQUEID", "Parcel_IMP2", "UNIQUEID", ["SUM"])
    arcpy.AddField_management(str(CoName) + "_Parcels_FTGtemp", "PCT_IMP", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.AddField_management(str(CoName) + "_Parcels_FTGtemp", "VALUE", "SHORT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(str(CoName) + "_Parcels_FTGtemp", "VALUE", "1", "PYTHON_9.3", "")
    arcpy.CalculateField_management(str(CoName) + "_Parcels_FTGtemp", "PCT_IMP","min([!VALUE!,((!SUM!/4046.86)/!ACRES2!)])","PYTHON_9.3")
    arcpy.Select_analysis(str(CoName) + "_Parcels_FTGtemp", str(CoName) + "_Parcels_FTG", 'PCT_IMP >= 0.1')
    arcpy.FeatureToRaster_conversion(str(CoName) + "_Parcels_FTG", "VALUE", str(CoName) + "_FTG_parcels", 1)
    arcpy.Delete_management("in_memory")
    print("--- TURF #4c Fractional Parcels Complete %s seconds ---" % (time.time() - start_time))

def turf_4d(CoName, CoGDB, DEV113, RTmask, ROW, INST, T_LANDUSE, TURFparcels):
    # TURF 4d: Mosaic available overlays to create Turf Mask with parcels
    start_time = time.time()
    inrasList = [ ]
    if arcpy.Exists(DEV113):
        inrasList.append(DEV113)
    if arcpy.Exists(RTmask):
        inrasList.append(RTmask)
    if arcpy.Exists(ROW):
        inrasList.append(ROW)
    if arcpy.Exists(INST):
        inrasList.append(INST)
    if arcpy.Exists(T_LANDUSE):
        inrasList.append(T_LANDUSE)
    if arcpy.Exists(TURFparcels):
        inrasList.append(TURFparcels)
    # print (inrasList)
    rasLocation = os.path.join(str(CoGDB))
    inrasList = str(";".join(inrasList)) #delimit by ";"
    arcpy.MosaicToNewRaster_management(inrasList,rasLocation,str(CoName) + "_TGmask","", "4_BIT", "1", "1", "LAST", "FIRST")
    arcpy.Delete_management("in_memory")
    print("--- TURF #4d Turf Mask with Parcels Complete %s seconds ---" % (time.time() - start_time))

def turf_4e(CoName, CoGDB, FTG_LU, FEDS_sm, FTGparcels):
	# TURF 4e: Mosaic available overlays to create FTG Mask with parcels
	start_time = time.time()
	inrasList = [ ]
	if arcpy.Exists(FTG_LU):
		inrasList.append(FTG_LU)
	if arcpy.Exists(FEDS_sm):
		inrasList.append(FEDS_sm)
	if arcpy.Exists(FTGparcels):
		inrasList.append(FTGparcels)
	# print (inrasList)
	rasLocation = os.path.join(str(CoGDB))
	inrasList = str(";".join(inrasList)) #delimit by ";"
	arcpy.MosaicToNewRaster_management(inrasList,rasLocation,str(CoName) + "_FTGmask","", "4_BIT", "1", "1", "LAST", "FIRST")
	arcpy.Delete_management("in_memory")
	print("--- TURF #4e Fractional Turf Mask with Parcels Complete %s seconds ---" % (time.time() - start_time))

def turf_5a(CoName, CoGDB, DEV113, RTmask, ROW, INST, T_LANDUSE):
    # TURF 5a: Mosaic available overlays to create Turf Mask without parcels
    start_time = time.time()
    inrasList = [ ]
    if arcpy.Exists(DEV113):
        inrasList.append(DEV113)
    if arcpy.Exists(RTmask):
        inrasList.append(RTmask)
    if arcpy.Exists(ROW):
        inrasList.append(ROW)
    if arcpy.Exists(INST):
        inrasList.append(INST)
    if arcpy.Exists(T_LANDUSE):
        inrasList.append(T_LANDUSE)
    # print (inrasList)
    rasLocation = os.path.join(str(CoGDB))
    inrasList = str(";".join(inrasList)) #delimit by ";"
    arcpy.MosaicToNewRaster_management(inrasList,rasLocation,str(CoName) + "_TGmask","", "4_BIT", "1", "1", "LAST", "FIRST")
    arcpy.Delete_management("in_memory")
    print("--- TURF #5a Turf Mask without Parcels Complete %s seconds ---" % (time.time() - start_time))

def turf_5b(CoName, CoGDB, FTG_LU, FEDS_sm):
	# TURF 5b: Mosaic available overlays to create FTG Mask without parcels
	start_time = time.time()
	inrasList = [ ]
	if arcpy.Exists(FTG_LU):
		inrasList.append(FTG_LU)
	if arcpy.Exists(FEDS_sm):
		inrasList.append(FEDS_sm)
	# print (inrasList)
	rasLocation = os.path.join(str(CoGDB))
	inrasList = str(";".join(inrasList)) #delimit by ";"
	arcpy.MosaicToNewRaster_management(inrasList,rasLocation,str(CoName) + "_FTGmask","", "4_BIT", "1", "1", "LAST", "FIRST")
	arcpy.Delete_management("in_memory")
	print("--- TURF #5b Fractional Turf Mask without Parcels Complete %s seconds ---" % (time.time() - start_time))


def turf_6(CoName, CoGDB, LuGDB, HERB, TGMask, TURFtemp):
    # TURF 6: Extract Herbaceous within Turf Mask and Reclass
    start_time = time.time()
    outExtractByMask = ExtractByMask(str(CoName) + "_Herb", str(CoName) + "_TGmask")
    outExtractByMask.save(str(CoGDB) + str(CoName) + "_TURFtemp")
    outSetNull = SetNull(str(CoName) + "_TURFtemp", "13", "VALUE = 0")
    outSetNull.save(str(LuGDB) + str(CoName) + "_TG_1m")
    print("--- TURF #6 Turf Grass Complete %s seconds ---" % (time.time() - start_time))

def frac_1(CoName, LuGDB, HERB, FTGMask, FTGtemp):
    # FRAC 1: Extract Herbaceous within FTG Mask and Reclass
    start_time = time.time()
    outExtractByMask = ExtractByMask(HERB, str(CoName) + "_FTGmask")
    outExtractByMask.save(str(CoName) + "_FTGtemp")
    outSetNull = SetNull(str(CoName) + "_FTGtemp", "11", "VALUE = 0")
    outSetNull.save(str(LuGDB) + str(CoName) + "_FTG_1m")
    print("--- FRAC #1 Fractional Turf Grass Complete %s seconds ---" % (time.time() - start_time))

def frac_2(CoName, LuGDB, FINR, HERB, FINRtemp):
    # FRAC 2: Extract Herbaceous within FINR Mask and Reclass
    if arcpy.Exists(FINR):
        try:
            arcpy.CalculateStatistics_management(FINR)
            outExtractByMask = ExtractByMask(HERB, FINR)
            outExtractByMask.save(str(CoName) + "_FINRtemp")
            outSetNull = SetNull(str(CoName) + "_FINRtemp", "12", "VALUE = 0")
            outSetNull.save(str(LuGDB) + str(CoName) + "_FINR_1m")
            print("--- FRAC #2 Fractional INR Complete ---")
        except:
            print("--- FRAC #2 Fractional INR Mask is Null ---")
    else:
        print("--- FRAC #2 Fractional INR Mask is Missing ---")

def for_1(CoName, DEV113, TC):
    # FOR 1: Identify Rural Core Areas of Tree Canopy over Pervious Surfaces
    start_time = time.time()
    RLTCP = Int(SetNull(Con(IsNull(DEV113),1) * TC <=0,Con(IsNull(DEV113),1) * TC))
    RLTCP.save("RLTCP")
    arcpy.CopyRaster_management("RLTCP", str(CoName) + "_RLTCP","","0","0","","","4_BIT","","","","")
    arcpy.Delete_management("RLTCP")
    arcpy.Delete_management("in_memory")
    print("--- FOR #1 RLTCP Creation Complete %s seconds ---" % (time.time() - start_time))

def for_2(CoName, TC, DEV27):
    # FOR 2: Define interface between Rural Core Areas and Edges of Developed Areas
    start_time = time.time()
    EDGE = Int(SetNull(Con(IsNull(DEV27),1,0) * TC <=0,Con(IsNull(DEV27),1,0) * TC))
    EDGE.save("EDGE")
    arcpy.CopyRaster_management("EDGE", str(CoName) + "_EDGE","","0","0","","","4_BIT","","","","")
    arcpy.Delete_management("EDGE")
    arcpy.Delete_management("in_memory")
    print("--- FOR #2 EDGE Creation Complete %s seconds ---" % (time.time() - start_time))

def for_3(CoName, CoGDB, RLTCP, EDGE):
    # FOR 3: Bleed/Expand Rural Core Areas to Edge of Developed Areas
    start_time = time.time()
    outCostDistance = CostDistance(str(CoName) + "_RLTCP", str(CoName) + "_EDGE", "", "", "", "", "", "")
    outCostDistance.save(str(CoGDB) + str(CoName) + "_CDEdge")
    arcpy.Delete_management("in_memory")
    print("--- FOR #3 Cost Distance Complete %s seconds ---" % (time.time() - start_time))

def for_4(CoName, DEV37, CDEdge):
    # FOR 4: Create Tree Canopy over Turf Grass Masks
    start_time = time.time()
    UrbMask = Int(Con(IsNull(str(CoName) + "_CDEdge"),1) * DEV37)
    UrbMask.save(str(CoName) + "_URBmask")
    RurMask = Int(Con(IsNull(str(CoName) + "_URBmask"),1))
    RurMask.save(str(CoName) + "_RURmask")
    arcpy.Delete_management("in_memory")
    print("--- FOR #4 TCT Masks Complete %s seconds ---" % (time.time() - start_time))

def for_5(CoName, DEV18, TC):
    # FOR 5: Rural and Urban TCT
    start_time = time.time()
    RurTCT = Int(Raster(str(CoName) + "_RURmask") * TC * DEV18) #Limits extent of tree canopy in rural areas
    RurTCT.save(str(CoName) + "_RUR_TCT")
    outTimes = Raster(str(CoName) + "_URBmask") * TC
    outTimes.save(str(CoName) + "_URB_TCT")
    arcpy.Delete_management("in_memory")
    print("--- FOR #5 Rural and Urban TCT Complete %s seconds ---" % (time.time() - start_time))

def for_6(CoName, CoGDB, LuGDB):
    # FOR 6: Final TCT (Mosaic to New Raster)
    start_time = time.time()
    rasLocation = str(CoGDB)
    inRasters = Raster(str(CoName) + "_URB_TCT"), Raster(str(CoName) + "_RUR_TCT")
    arcpy.MosaicToNewRaster_management(inRasters,rasLocation,str(CoName) + "_TCT1","", "4_BIT", "1", "1", "LAST", "FIRST")
    outReclassify = Con(Raster(str(CoName) + "_TCT1") ==1,9)
    outReclassify.save(str(LuGDB) + str(CoName) + "_TCT_1m")
    TCT = os.path.join(str(LuGDB) + str(CoName) + "_TCT_1m")
    arcpy.Delete_management("in_memory")
    print("--- FOR #6 Tree Cover over Turf Complete %s seconds ---" % (time.time() - start_time))

def for_7(CoName, TCT, TC):
    # FOR 7: Identify Potential Forests
    start_time = time.time()
    NonTCT = Int(Con(IsNull(TCT),1))
    NonTCT.save(str(CoName) + "_nonTCT")
    outTimes1 = TC * Raster(str(CoName) + "_nonTCT")
    outTimes1.save(str(CoName) + "_potFOR")
    arcpy.Delete_management("in_memory")
    print("--- FOR #7 Potential Forest Complete %s seconds ---" % (time.time() - start_time))

    ############################# WETLAND SUBMODEL #############################
    
	###Chesapeake Conservancy & PA Wetlands###

def wet_1_ccpa(CoName, CoGDB, LuGDB, fc_Tidal, ccpa_wetlands, nwi_Tidal):
    # WET 1: Creating Tidal Raster
	if arcpy.Exists(nwi_Tidal):
		start_time = time.time()
		output = os.path.join(str(CoGDB), str(CoName) +"_mask_tidal_diss")
		arcpy.Dissolve_management(fc_Tidal, output, "WETCLASS")
		extractTidal = ExtractByMask(ccpa_wetlands, output)
		input_rasters = nwi_Tidal; extractTidal
		arcpy.MosaicToNewRaster_management (input_rasters, str(LuGDB), str(CoName) + "_WLT_1m", "", "4_BIT", "1", "1", "FIRST", "")
		arcpy.Delete_management(extractTidal)
		arcpy.Delete_management("in_memory")
		print("--- WET #1 Tidal Raster Created Complete %s seconds ---" % (time.time() - start_time))
	else:
		print ("WET #1 No NWI Tidal Raster Exists")

def wet_2_ccpa(CoName, CoGDB, LuGDB, fc_FPlain, ccpa_wetlands, nwi_FPlain):
    # WET 2: Creating Flood Plain Raster
	if arcpy.Exists(nwi_FPlain):
		start_time = time.time()
		output = os.path.join(str(CoGDB), str(CoName) +"_mask_fplain_diss")
		arcpy.Dissolve_management(fc_FPlain, output, "WETCLASS")
		extractFPlain = ExtractByMask(ccpa_wetlands, output)
		nwiFP = Con(Raster(nwi_FPlain)==2,1)
		input_rasters = nwiFP; extractFPlain
		arcpy.MosaicToNewRaster_management (input_rasters, str(LuGDB), str(CoName) + "_WLF_1m", "", "4_BIT", "1", "1", "FIRST", "")
		arcpy.Delete_management(extractFPlain)
		arcpy.Delete_management("in_memory")
		print("--- WET #2 Flood Plain Raster Created Complete %s seconds ---" % (time.time() - start_time))
	else:
		print ("WET #2 No NWI Flood Plain Raster Exists")


def wet_3_ccpa(CoName, CoGDB, LuGDB, fc_OTHWL, ccpa_wetlands, nwi_OTHWL):
    # WET 3: Creating Other Wetland Raster
	if arcpy.Exists(nwi_OTHWL):
		start_time = time.time()
		output = os.path.join(str(CoGDB), str(CoName) +"_mask_oth_wl_diss")
		arcpy.Dissolve_management(fc_OTHWL, output, "WETCLASS")
		extractOTH_WL = ExtractByMask(ccpa_wetlands, output)
		nwiOTH = Con(Raster(nwi_OTHWL)==3,1)
		input_rasters = nwiOTH; extractOTH_WL
		arcpy.MosaicToNewRaster_management (input_rasters, str(LuGDB), str(CoName) + "_WLO_1m", "", "4_BIT", "1", "1", "FIRST", "")
		arcpy.Delete_management(extractOTH_WL)
		arcpy.Delete_management("in_memory")
		print("--- WET #3 Other Wetland Raster Created Complete %s seconds ---" % (time.time() - start_time))
	else:
		print ("WET #3 No NWI Other Wetland Raster Exists")

	###Chesapeake Conservancy Wetlands###

def wet_1_cc(CoName, CoGDB, LuGDB, fc_Tidal, cc_wetlands, nwi_Tidal):
	# WET 1: Creating Tidal Raster
	if arcpy.Exists(nwi_Tidal):
		start_time = time.time()
		output = os.path.join(str(CoGDB), str(CoName) +"_mask_tidal_diss")
		arcpy.Dissolve_management(fc_Tidal, output, "WETCLASS")
		extractTidal = ExtractByMask(cc_wetlands, output)
		input_rasters = nwi_Tidal; extractTidal
		arcpy.MosaicToNewRaster_management (input_rasters, str(LuGDB), str(CoName) + "_WLT_1m", "", "4_BIT", "1", "1", "FIRST", "")
		arcpy.Delete_management(extractTidal)
		arcpy.Delete_management("in_memory")
		print("--- WET #1 Tidal Raster Created Complete %s seconds ---" % (time.time() - start_time))
	else:
		print ("WET #1 No NWI Tidal Raster Exists")

def wet_2_cc(CoName, CoGDB, LuGDB, fc_FPlain, cc_wetlands, nwi_FPlain):
	# WET 2: Creating Flood Plain Raster
	if arcpy.Exists(nwi_FPlain):
		start_time = time.time()
		output = os.path.join(str(CoGDB), str(CoName) +"_mask_fplain_diss")
		arcpy.Dissolve_management(fc_FPlain, output, "WETCLASS")
		extractFPlain = ExtractByMask(cc_wetlands, output)
		nwiFP = Con(Raster(nwi_FPlain)==2,1)
		input_rasters = nwiFP; extractFPlain
		arcpy.MosaicToNewRaster_management (input_rasters, str(LuGDB), str(CoName) + "_WLF_1m", "", "4_BIT", "1", "1", "FIRST", "")
		arcpy.Delete_management(extractFPlain)
		arcpy.Delete_management("in_memory")
		print("--- WET #2 Flood Plain Raster Created Complete %s seconds ---" % (time.time() - start_time))
	else:
		print ("WET #2 No NWI Flood Plain Raster Exists")

def wet_3_cc(CoName, CoGDB, LuGDB, fc_OTHWL, cc_wetlands, nwi_OTHWL):
	# WET 3: Creating Other Wetland Raster
	if arcpy.Exists(nwi_OTHWL):
		start_time = time.time()
		output = os.path.join(str(CoGDB), str(CoName) +"_mask_oth_wl_diss")
		arcpy.Dissolve_management(fc_OTHWL, output, "WETCLASS")
		extractOTH_WL = ExtractByMask(cc_wetlands, output)
		nwiOTH = Con(Raster(nwi_OTHWL)==3,1)
		input_rasters = nwiOTH; extractOTH_WL
		arcpy.MosaicToNewRaster_management (input_rasters, str(LuGDB), str(CoName) + "_WLO_1m", "", "4_BIT", "1", "1", "FIRST", "")
		arcpy.Delete_management(extractOTH_WL)
		arcpy.Delete_management("in_memory")
		print("--- WET #3 Other Wetland Raster Created Complete %s seconds ---" % (time.time() - start_time))
	else:
		print ("WET #3 No NWI Other Wetland Raster Exists")

	###PA Wetlands###

def wet_1_pa(CoName, CoGDB, LuGDB, fc_Tidal, pa_wetlands, nwi_Tidal):
	# WET 1: Creating Tidal Raster
	if arcpy.Exists(nwi_Tidal):
		start_time = time.time()
		output = os.path.join(str(CoGDB), str(CoName) +"_mask_tidal_diss")
		arcpy.Dissolve_management(fc_Tidal, output, "WETCLASS")
		extractTidal = ExtractByMask(pa_wetlands, output)
		input_rasters = nwi_Tidal; extractTidal
		arcpy.MosaicToNewRaster_management (input_rasters, str(LuGDB), str(CoName) + "_WLT_1m", "", "4_BIT", "1", "1", "FIRST", "")
		arcpy.Delete_management(extractTidal)
		arcpy.Delete_management("in_memory")
		print("--- WET #1 Tidal Raster Created Complete %s seconds ---" % (time.time() - start_time))
	else:
		print ("WET #1 No NWI Tidal Raster Exists")

def wet_2_pa(CoName, CoGDB, LuGDB, fc_FPlain, pa_wetlands, nwi_FPlain):
	# WET 2: Creating Flood Plain Raster
	if arcpy.Exists(nwi_FPlain):
		start_time = time.time()
		output = os.path.join(str(CoGDB), str(CoName) +"_mask_fplain_diss")
		arcpy.Dissolve_management(fc_FPlain, output, "WETCLASS")
		extractFPlain = ExtractByMask(pa_wetlands, output)
		nwiFP = Con(Raster(nwi_FPlain)==2,1)
		input_rasters = nwiFP; extractFPlain
		arcpy.MosaicToNewRaster_management (input_rasters, str(LuGDB), str(CoName) + "_WLF_1m", "", "4_BIT", "1", "1", "FIRST", "")
		arcpy.Delete_management(extractFPlain)
		arcpy.Delete_management("in_memory")
		print("--- WET #2 Flood Plain Raster Created Complete %s seconds ---" % (time.time() - start_time))
	else:
		print ("WET #2 No NWI Flood Plain Raster Exists")

def wet_3_pa(CoName, CoGDB, LuGDB, fc_OTHWL, pa_wetlands, nwi_OTHWL):
	# WET 3: Creating Other Wetland Raster
	if arcpy.Exists(nwi_OTHWL):
		start_time = time.time()
		output = os.path.join(str(CoGDB), str(CoName) +"_mask_oth_wl_diss")
		arcpy.Dissolve_management(fc_OTHWL, output, "WETCLASS")
		extractOTH_WL = ExtractByMask(pa_wetlands, output)
		nwiOTH = Con(Raster(nwi_OTHWL)==3,1)
		input_rasters = nwiOTH; extractOTH_WL
		arcpy.MosaicToNewRaster_management (input_rasters, str(LuGDB), str(CoName) + "_WLO_1m", "", "4_BIT", "1", "1", "FIRST", "")
		arcpy.Delete_management(extractOTH_WL)
		arcpy.Delete_management("in_memory")
		print("--- WET #3 Other Wetland Raster Created Complete %s seconds ---" % (time.time() - start_time))
	else:
		print ("WET #3 No NWI Other Wetland Raster Exists")

def for_8(CoName, CoGDB, LuGDB, TC, WAT, WLF, WLO, WLT, WAT_FOR, POT_FOR):
    # FOR 8: Separate Mixed Open Trees from Potential Forests considering adjacent natural land uses
    start_time = time.time()
    WLF = os.path.join(str(LuGDB),str(CoName) + "_WLF_1m")
    WLO = os.path.join(str(LuGDB),str(CoName) + "_WLO_1m")
    WLT = os.path.join(str(LuGDB),str(CoName) + "_WLT_1m")
    outCon = Con(Raster(WAT)==3,1)
    outCon.save(str(CoName) + "_watFOR")
    WAT_FOR = os.path.join(str(CoGDB),str(CoName) + "_watFOR")
    POT_FOR = os.path.join(str(CoGDB),str(CoName) + "_potFOR")

    print("WLF", arcpy.Exists(WLF))
    print("WLO", arcpy.Exists(WLO))
    print("WLT", arcpy.Exists(WLT))
    print("WAT_FOR", arcpy.Exists(WAT_FOR))
    print("POT_FOR", arcpy.Exists(POT_FOR))

    inrasList = [ ]
    if arcpy.Exists(WLT):
        inrasList.append(WLT)
    if arcpy.Exists(WLF):
        inrasList.append(WLF)
    if arcpy.Exists(WLO):
        inrasList.append(WLO)
    if arcpy.Exists(WAT_FOR):
        inrasList.append(WAT_FOR)
    if arcpy.Exists(POT_FOR):
        inrasList.append(POT_FOR)

    print (inrasList)
    inrasList = str(";".join(inrasList)) #delimit by ";"
    rasLocation = os.path.join(str(CoGDB))
    arcpy.MosaicToNewRaster_management(inrasList,rasLocation,str(CoName) + "_NATnhbrs","","4_BIT", "1", "1", "LAST", "FIRST")
    outRegionGrp = RegionGroup(Raster(str(CoName) + "_NATnhbrs"),"EIGHT","WITHIN","NO_LINK","0")
    outRegionGrp.save(str(CoName) + "_ForRG")
    outCon = Con(str(CoName) + "_ForRG", 1, "", "VALUE > 0 AND COUNT >= 4047")
    outExtractByMask = ExtractByMask(TC,outCon)
    outCon2 = Con(outExtractByMask==1,8)
    outCon2.save(str(LuGDB) + str(CoName) + "_FOR_1m")
    outCon3 = Con(str(CoName) + "_ForRG",1,"", "VALUE > 0 AND COUNT < 4047")
    outExtractByMask = ExtractByMask(TC,outCon3)
    outExtractByMask.save(str(CoName) + "_MOTrees")
    arcpy.Delete_management("in_memory")
    print("--- FOR #8 Forest and Mixed Open Trees Complete %s seconds ---" % (time.time() - start_time))

def mo_1(CoName, CoGDB, LuGDB, TREES, SS):
    start_time = time.time()
    inrasList = [ ]
    if arcpy.Exists(TREES):
        inrasList.append(TREES)
    if arcpy.Exists(SS):
        inrasList.append(SS)
    rasLocation = os.path.join(str(CoGDB))
    inrasList = str(";".join(inrasList)) #delimit by ";"
    arcpy.MosaicToNewRaster_management(inrasList,rasLocation,str(CoName) + "_MOtemp","", "4_BIT", "1", "1", "LAST", "FIRST")
    outSetNull = SetNull(str(CoName) + "_MOtemp", "10", "VALUE = 0")
    outSetNull.save(str(LuGDB) + str(CoName) + "_MO_1m")
    arcpy.Delete_management("in_memory")
    print("--- MO #1 Mixed Open Complete %s seconds ---" % (time.time() - start_time))

def mo_2a(CoName, CoGDB, inrasListMO):
    # MO 2: Create Mixed Open with Ancillary Data
    # Step 2a: Create Potential Mixed Open Area
    start_time = time.time()
    rasLocation = os.path.join(str(CoGDB))
    inrasList = str(";".join(inrasListMO)) #delimit by ";"
    arcpy.MosaicToNewRaster_management(inrasList,rasLocation,str(CoName) + "_MOspace","", "4_BIT", "1", "1", "LAST", "FIRST")
    arcpy.Delete_management("in_memory")
    print("--- MO #2a MOspace Complete %s seconds ---" % (time.time() - start_time))

def mo_2b(CoName, CoGDB, BAR, LV):
    # MO 2b: Create Herbaceous Layer
    if arcpy.Exists(str(CoName) + "_Herb"):
        print("Herbaceous Layer Exists")
    else:
        start_time = time.time()
        rasLocation = os.path.join(str(CoGDB))
        inRasters = Raster(BAR),Raster(LV)
        arcpy.MosaicToNewRaster_management(inRasters,rasLocation,str(CoName) + "_Herb","", "4_BIT", "1", "1", "LAST", "FIRST")
        arcpy.Delete_management("in_memory")
        print("--- MO #2b Herbaceous Mosaic Complete %s seconds ---" % (time.time() - start_time))

    return HERB

def mo_2c(CoName, CoGDB, HERB, MOherb):
    # MO 2c: Extract Herbaceous within MOspace.
    start_time = time.time()
    inRaster = Raster(HERB)
    inMaskData = Raster(str(CoName) + "_MOspace")
    outExtractByMask = ExtractByMask(inRaster, inMaskData)
    outExtractByMask.save(str(CoName) + "_MOherb")
    arcpy.Delete_management("in_memory")
    MOherb = os.path.join(str(CoGDB) + str(CoName) + "_MOherb")
    print("--- MO #2c Extract MOherb Complete %s seconds ---" % (time.time() - start_time))

    return MOherb

def mo_2d(CoName, CoGDB, LuGDB, MOherb, TREES, SS):
    # MO 2d: Final Mixed Open (mosaic)
    inrasList = [ ]
    if arcpy.Exists(TREES):
        inrasList.append(TREES)
    if arcpy.Exists(SS):
        inrasList.append(SS)
    if arcpy.Exists(MOherb):
        inrasList.append(MOherb)
    start_time = time.time()
    rasLocation = os.path.join(str(CoGDB))
    inrasList = str(";".join(inrasList)) #delimit by ";"
    arcpy.MosaicToNewRaster_management(inrasList, rasLocation, str(CoName) + "_MOtemp","", "4_BIT", "1", "1", "LAST", "FIRST")
    outSetNull = SetNull(str(CoName) + "_MOtemp", "10", "VALUE = 0")
    outSetNull.save(str(LuGDB) + str(CoName) + "_MO_1m")
    arcpy.Delete_management("in_memory")
    print("--- MO #2d Mixed Open Complete %s seconds ---" % (time.time() - start_time))


def final_2_3(CoName, CoGDB, IR, INR, TCI, WAT, WLT, WLF, WLO, FOR, TCT, MO, FTG, FINR, TG):
    # Final 2: Reclass Input Rasters to Appropriate Mosaic Hierarchical Values.
    start_time = time.time()
    TCI2 = Con(Raster(TCI)==1,3)
    WAT2 = Con(Raster(WAT)==3,4)
    if arcpy.Exists(WLT):
        WLT2 = Con(Raster(WLT)==1,5)
    if arcpy.Exists(WLF):
        WLF2 = Con(Raster(WLF)==1,6)
    if arcpy.Exists(WLO):
        WLO2 = Con(Raster(WLO)==1,7)
    print("--- Final #2 Preprocessing Complete %s seconds ---" % (time.time() - start_time))

    # Final 3: Mosaic All 1m Rasters
    LUlist = [ ]
    if arcpy.Exists(IR):
        LUlist.append(IR)
    if arcpy.Exists(INR):
        LUlist.append(INR)
    if arcpy.Exists(TCI2):
        LUlist.append(TCI2)
    if arcpy.Exists(WAT2):
        LUlist.append(WAT2)
    if arcpy.Exists(WLT):  # use WLT because WLT2 is only defined if WLT exists
        LUlist.append(WLT2)
    if arcpy.Exists(WLF):
        LUlist.append(WLF2)
    if arcpy.Exists(WLO):
        LUlist.append(WLO2)
    if arcpy.Exists(FOR):
        LUlist.append(FOR)
    if arcpy.Exists(TCT):
        LUlist.append(TCT)
    if arcpy.Exists(MO):
        LUlist.append(MO)
    if arcpy.Exists(FTG):
        LUlist.append(FTG)
    if arcpy.Exists(FINR):
        LUlist.append(FINR)
    if arcpy.Exists(TG):
        LUlist.append(TG)

    start_time = time.time()
    rasLocation = os.path.join(str(CoGDB))
    outCellStats = CellStatistics(LUlist, "MINIMUM", "DATA") # LUlist must be used directly as inRasters because it has the correct format needed for CellStatistics, else 000732 error.
    arcpy.Delete_management(str(CoGDB) + str(CoName) + "_Mosaic")
    outCellStats.save(str(CoGDB) + str(CoName) + "_Mosaic")
    arcpy.Delete_management("in_memory")
    print("--- Final #3 Non-Ag Mosaic Complete %s seconds ---" % (time.time() - start_time))

def final_4(CoName, CoGDB, LuGDB, TempGDB, Temp10GDB, TempDirectory, Snap):
    # Final 4: Split Mosaic and Reclass Land Uses to [1,0]
    start_time = time.time()
    arcpy.env.workspace = Temp10GDB
    arcpy.env.scratchWorkspace = Temp10GDB
    arcpy.env.snapRaster = Snap
    arcpy.env.extent = Snap
    
    LuTable = os.path.join(str(TempDirectory), str(CoName) + "_LuTable.dbf") #define LuTable
    if arcpy.Exists(LuTable):
        arcpy.Delete_management(str(TempDirectory), str(CoName) + "_LuTable.dbf")
        print ("Existing LuTable Deleted")
    else: 
        arcpy.TableToTable_conversion(str(CoGDB) + str(CoName) + "_Mosaic", str(TempDirectory), str(CoName) + "_LuTable")
        LuTable = os.path.join(str(TempDirectory), str(CoName) + "_LuTable.dbf")
    arcpy.JoinField_management(LuTable,"Value","D:/B__P6_Analyst/ClassNames.dbf","Value",["Class_Name"])
    rows = arcpy.SearchCursor(LuTable, "", "", "", "")
    for row in rows:
        luAbr = row.getValue("Class_Name")
        luClass = row.getValue("Value")
        sqlQuery = "Value = " + str(luClass)
        print (sqlQuery)
        rasExtract = ExtractByAttributes(str(CoGDB) + str(CoName) + "_Mosaic", sqlQuery)
        outCon = Con(IsNull(rasExtract),0,1)
        outAgg = Aggregate(outCon, 10, "SUM", "TRUNCATE", "DATA")
        outAgg.save(str(Temp10GDB) + str(CoName) + "_" + str(luAbr) + "_10m")
    outCon2 = Con(IsNull(str(CoGDB) + str(CoName) + "_Mosaic"),1,0)
    outCon3 = Con(IsNull(str(CoGDB) + str(CoName) + "_Mosaic"),14,str(CoGDB) + str(CoName) + "_Mosaic")
    xMosaic = arcpy.sa.ExtractByMask(outCon3,str(LuGDB) + str(CoName) + "_LC")
    xMosaic.save(str(LuGDB) + str(CoName) + "_Mosaic") #1m land use mosaic with nulls set to AgSpace
    print("All Done")

    arcpy.env.snapRaster = Snap #location of the 10m snap raster
    outAgg2 = Aggregate(outCon2, 10, "SUM", "TRUNCATE", "DATA")
    outAgg2.save(str(Temp10GDB) + str(CoName) + "_" + "AG_10m")
    print("--- Final #4: All Land Uses Split and Reclassed  %s seconds ---" % (time.time() - start_time))

def final_5(CoName, Temp10GDB, Snap):
    # Final 5: Combine all 10m rasters (8-10 minutes)
    arcpy.env.snapRaster = Snap
    arcpy.env.extent = Snap
    start_time = time.time()
    IR = os.path.join(str(Temp10GDB) + str(CoName) + "_IR_10m")
    INR = os.path.join(str(Temp10GDB) + str(CoName) + "_INR_10m")
    TCI = os.path.join(str(Temp10GDB) + str(CoName) + "_TCI_10m")
    WAT = os.path.join(str(Temp10GDB) + str(CoName) + "_WAT_10m")
    WLT = os.path.join(str(Temp10GDB) + str(CoName) + "_WLT_10m")
    WLF = os.path.join(str(Temp10GDB) + str(CoName) + "_WLF_10m")
    WLO = os.path.join(str(Temp10GDB) + str(CoName) + "_WLO_10m")
    FOR = os.path.join(str(Temp10GDB) + str(CoName) + "_FOR_10m")
    TCT = os.path.join(str(Temp10GDB) + str(CoName) + "_TCT_10m")
    MO = os.path.join(str(Temp10GDB) + str(CoName) + "_MO_10m")
    FTG = os.path.join(str(Temp10GDB) + str(CoName) + "_FTG_10m")
    FINR = os.path.join(str(Temp10GDB) + str(CoName) + "_FINR_10m")
    TG = os.path.join(str(Temp10GDB) + str(CoName) + "_TG_10m")
    AG = os.path.join(str(Temp10GDB) + str(CoName) + "_AG_10m")
    crpCDL = os.path.join(str(Temp10GDB) + str(CoName) + "_crpCDL")
    pasCDL = os.path.join(str(Temp10GDB) + str(CoName) + "_pasCDL")
    DEMstrm = os.path.join(str(Temp10GDB) + str(CoName) + "_Stream")
    outCon = Con(IsNull(DEMstrm),0,DEMstrm)
    outCon.save(str(Temp10GDB) + str(CoName) + "_NewStrm")
    NewStrm = os.path.join(str(Temp10GDB) + str(CoName) + "_NewStrm")

    print ("IR", arcpy.Exists(IR))
    print ("INR", arcpy.Exists(INR))
    print ("WAT", arcpy.Exists(WAT))
    print ("WLT", arcpy.Exists(WLT))
    print ("WLF", arcpy.Exists(WLF))
    print ("WLO", arcpy.Exists(WLO))
    print ("FOR", arcpy.Exists(FOR))
    print ("TCI", arcpy.Exists(TCI))
    print ("TCT", arcpy.Exists(TCT))
    print ("MO", arcpy.Exists(MO))
    print ("FTG", arcpy.Exists(FTG))
    print ("FINR", arcpy.Exists(FINR))
    print ("TG", arcpy.Exists(TG))
    print ("AG", arcpy.Exists(AG))
    print ("crpCDL", arcpy.Exists(crpCDL))
    print ("pasCDL", arcpy.Exists(pasCDL))
    print ("NewStrm", arcpy.Exists(NewStrm))

    # If-check to see if all rasters are present
    combList = []
    if arcpy.Exists(IR):
        combList.append(IR)
    if arcpy.Exists(INR):
        combList.append(INR)
    if arcpy.Exists(TCI):
        combList.append(TCI)
    if arcpy.Exists(WAT):
        combList.append(WAT)
    if arcpy.Exists(WLT):
        combList.append(WLT)
    if arcpy.Exists(WLF):
        combList.append(WLF)
    if arcpy.Exists(WLO):
        combList.append(WLO)
    if arcpy.Exists(FOR):
        combList.append(FOR)
    if arcpy.Exists(TCT):
        combList.append(TCT)
    if arcpy.Exists(MO):
        combList.append(MO)
    if arcpy.Exists(FTG):
        combList.append(FTG)
    if arcpy.Exists(FINR):
        combList.append(FINR)
    if arcpy.Exists(TG):
        combList.append(TG)
    if arcpy.Exists(AG):
        combList.append(AG)
    if arcpy.Exists(crpCDL):
        combList.append(crpCDL)
    if arcpy.Exists(pasCDL):
        combList.append(pasCDL)
    if arcpy.Exists(NewStrm):
        combList.append(NewStrm)

    outCombine = Combine(combList)
    outCombine.save(str(Temp10GDB) + str(CoName) + "_Combo")
    arcpy.Delete_management("in_memory")
    print("--- Final #5: Combine Complete  %s seconds ---" % (time.time() - start_time))

    return outCombine

def final_6(CoName, Temp10GDB, FINR, WLT, WLF, Snap):
    # Final 6: Rename, Create, and Calculate Fields (~ 25 minutes)
    arcpy.env.snapRaster = Snap
    arcpy.env.extent = Snap
    start_time = time.time()
    arcpy.TableToTable_conversion(str(Temp10GDB) + str(CoName) + "_Combo", str(Temp10GDB), "Combo")
    Combo = str(Temp10GDB) + "Combo"
    for field in arcpy.ListFields(Combo,"*_*"):
        old_field = field.name
        new_field = old_field.split("_",3)[2]
        print(old_field,new_field)
        arcpy.AlterField_management(Combo,old_field,new_field)
    arcpy.AddField_management(Combo, "INR_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "MO_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "TG_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "WAT_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "CRP_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "PAS_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "DIFF_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "NAT", "DOUBLE","5")
    arcpy.AddField_management(Combo, "WAT_2", "DOUBLE","5")
    arcpy.AddField_management(Combo, "WLT_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "WLF_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "WLO_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "FOR_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "TCT_1", "DOUBLE","5")
    arcpy.AddField_management(Combo, "TG_2", "DOUBLE","5")
    arcpy.AddField_management(Combo, "CRP_2", "DOUBLE","5")
    arcpy.AddField_management(Combo, "PAS_2", "DOUBLE","5")
    arcpy.AddField_management(Combo, "DIFF_2", "DOUBLE","5")
    arcpy.AddField_management(Combo, "MO_2", "DOUBLE","5")
    arcpy.AddField_management(Combo, "MO_3", "DOUBLE","5")
    arcpy.AddField_management(Combo, "TG_3", "DOUBLE","5")

    if arcpy.Exists(FINR):
        arcpy.CalculateField_management(Combo, "MO_1", "(!FTG! * 0.3) + (!FINR! * 0.7) + !MO!","PYTHON_9.3")
        arcpy.CalculateField_management(Combo, "INR_1","(!FINR!*0.3) + !INR!","PYTHON_9.3")
    else:
        arcpy.CalculateField_management(Combo, "MO_1", "(!FTG! * 0.3) + !MO!","PYTHON_9.3")
        arcpy.CalculateField_management(Combo, "INR_1","!INR!","PYTHON_9.3")
    arcpy.CalculateField_management(Combo, "TG_1","(!FTG! *0.7) + !TG!","PYTHON_9.3")
    arcpy.CalculateField_management(Combo, "WAT_1","max(!WAT!,!NewSt!)","PYTHON_9.3")
    arcpy.CalculateField_management(Combo, "CRP_1","(!AG! - (((!AG! * !crpCD!)/100) + ((!AG! * !pasCD!)/100)))*0.5 + (!AG! * !crpCD!)/100","PYTHON_9.3")
    arcpy.CalculateField_management(Combo, "PAS_1","(!AG! - (((!AG! * !pasCD!)/100) + ((!AG! * !crpCD!)/100)))*0.5 + (!AG! * !pasCD!)/100","PYTHON_9.3")
    if arcpy.Exists(WLT) and arcpy.Exists(WLF):
        arcpy.CalculateField_management(Combo, "DIFF_1", "abs(100 - (!IR!+ !INR_1!+ !WAT_1! + !WLT! + !WLF! + !WLO! + !FOR_! + !TCI! + !TCT! + !MO_1! + !TG_1! + !CRP_1! + !PAS_1!))","PYTHON_9.3")
        arcpy.CalculateField_management(Combo, "NAT", "(!WLT! + !WLF! + !WLO! + !FOR_! + !TCT! + !MO_1! + !TG_1! + !CRP_1! + !PAS_1!)","PYTHON_9.3")
    elif arcpy.Exists(WLF):
        arcpy.CalculateField_management(Combo, "DIFF_1", "abs(100 - (!IR!+ !INR_1!+ !WAT_1! + !WLF! + !WLO! + !FOR_! + !TCI! + !TCT! + !MO_1! + !TG_1! + !CRP_1! + !PAS_1!))","PYTHON_9.3")
        arcpy.CalculateField_management(Combo, "NAT", "(!WLF! + !WLO! + !FOR_! + !TCT! + !MO_1! + !TG_1! + !CRP_1! + !PAS_1!)","PYTHON_9.3")
    else:
        arcpy.CalculateField_management(Combo, "DIFF_1", "abs(100 - (!IR!+ !INR_1!+ !WAT_1! + !WLO! + !FOR_! + !TCI! + !TCT! + !MO_1! + !TG_1! + !CRP_1! + !PAS_1!))","PYTHON_9.3")
        arcpy.CalculateField_management(Combo, "NAT", "(!WLO! + !FOR_! + !TCT! + !MO_1! + !TG_1! + !CRP_1! + !PAS_1!)","PYTHON_9.3")

    # Zero out streams if no natural land is available to accommodate them
    arcpy.MakeTableView_management(Combo,"Subset",field_info = "fieldinfo")
    arcpy.SelectLayerByAttribute_management("Subset", 'NEW_SELECTION', 'NAT = 0 or DIFF_1 = 0')
    arcpy.CalculateField_management("Subset", "WAT_2","!WAT!","PYTHON_9.3")
    if arcpy.Exists(WLT):
        arcpy.CalculateField_management("Subset", "WLT_1","!WLT!","PYTHON_9.3")
    if arcpy.Exists(WLF):
        arcpy.CalculateField_management("Subset", "WLF_1","!WLF!","Python_9.3")
    arcpy.CalculateField_management("Subset", "WLO_1","!WLO!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "FOR_1","!FOR_!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "TCT_1","!TCT!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "TG_2","!TG_1!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "TG_3","!TG_1!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "CRP_2","!CRP_1!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "PAS_2","!PAS_1!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "MO_2","!MO_1!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "MO_3","!MO_1!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "DIFF_2","0","PYTHON_9.3")
    arcpy.SelectLayerByAttribute_management("Subset","CLEAR_SELECTION")

    # Zero out natural land uses if stream area exceeds available natural area.
    arcpy.SelectLayerByAttribute_management("Subset", 'NEW_SELECTION', 'NAT > 0 and DIFF_1 >= NAT')
    arcpy.CalculateField_management("Subset", "WAT_2","(!WAT_1! + (!NAT! - !DIFF_1!))","PYTHON_9.3") # max of WAT and WAT_1
    if arcpy.Exists(WLT):
        arcpy.CalculateField_management("Subset", "WLT_1","0","PYTHON_9.3")
    if arcpy.Exists(WLF):
        arcpy.CalculateField_management("Subset", "WLF_1","0","Python_9.3")
    arcpy.CalculateField_management("Subset", "WLO_1","0","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "FOR_1","0","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "TCT_1","0","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "TG_2","0","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "TG_3","0","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "CRP_2","0","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "PAS_2","0","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "MO_2","0","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "MO_3","0","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "DIFF_2","0","PYTHON_9.3")
    arcpy.SelectLayerByAttribute_management("Subset","CLEAR_SELECTION")

    # Distribute deductions proportionally to natural land uses
    arcpy.SelectLayerByAttribute_management("Subset", 'NEW_SELECTION', 'NAT > 0 and DIFF_1 < NAT')
    arcpy.CalculateField_management("Subset", "WAT_2","!WAT_1!","PYTHON_9.3")
    if arcpy.Exists(WLT):
        arcpy.CalculateField_management("Subset", "WLT_1","round(!WLT! - !DIFF_1! * !WLT!/!NAT!)","PYTHON_9.3")
    if arcpy.Exists(WLF):
        arcpy.CalculateField_management("Subset", "WLF_1","round(!WLF! - !DIFF_1! * !WLF!/!NAT!)","Python_9.3")
    arcpy.CalculateField_management("Subset", "WLO_1","round(!WLO! - !DIFF_1! * !WLO!/!NAT!)","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "FOR_1","round(!FOR_! - !DIFF_1! * !FOR_!/!NAT!)","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "TCT_1","round(!TCT! - !DIFF_1! * !TCT!/!NAT!)","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "MO_2","round(!MO_1! - !DIFF_1! * !MO_1!/!NAT!)","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "TG_2","round(!TG_1! - !DIFF_1! * !TG_1!/!NAT!)","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "CRP_2","round(!CRP_1! - !DIFF_1! * !CRP_1!/!NAT!)","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "PAS_2","round(!PAS_1! - !DIFF_1! * !PAS_1!/!NAT!)","PYTHON_9.3")

    if arcpy.Exists(WLT) and arcpy.Exists(WLF):
        arcpy.CalculateField_management("Subset", "DIFF_2", "(100 - (!IR! + !INR_1! + !WAT_2! + !WLT_1! + !WLF_1! + !WLO_1! + !FOR_1! + !TCI! + !TCT_1! + !MO_2! + !TG_2! + !CRP_2! + !PAS_2!))","PYTHON_9.3")
    elif arcpy.Exists(WLF):
        arcpy.CalculateField_management("Subset", "DIFF_2", "(100 - (!IR! + !INR_1! + !WAT_2! + !WLF_1! + !WLO_1! + !FOR_1! + !TCI! + !TCT_1! + !MO_2! + !TG_2! + !CRP_2! + !PAS_2!))","PYTHON_9.3")
    else:
        arcpy.CalculateField_management("Subset", "DIFF_2", "(100 - (!IR! + !INR_1! + !WAT_2! + !WLO_1! + !FOR_1! + !TCI! + !TCT_1! + !MO_2! + !TG_2! + !CRP_2! + !PAS_2!))","PYTHON_9.3")

    # Correct for rounding errors
    arcpy.CalculateField_management("Subset", "MO_3","!MO_2!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "TG_3","!TG_2!","PYTHON_9.3")

    arcpy.SelectLayerByAttribute_management("Subset", 'NEW_SELECTION', 'WAT_1 > 0 and DIFF_2 <> 0')
    arcpy.CalculateField_management("Subset", "WAT_2","max(0,!WAT_1! + !DIFF_2!)","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "MO_3","!MO_2!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "TG_3","!TG_2!","PYTHON_9.3")

    arcpy.SelectLayerByAttribute_management("Subset", 'NEW_SELECTION', 'WAT_1 = 0 and DIFF_2 <> 0 and MO_2 >= TG_2')
    arcpy.CalculateField_management("Subset", "MO_3","max(0,!MO_2! + !DIFF_2!)","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "TG_3","!TG_2!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "WAT_2","!WAT_1!","PYTHON_9.3")

    arcpy.SelectLayerByAttribute_management("Subset", 'NEW_SELECTION', 'WAT_1 = 0 and DIFF_2 <> 0 and TG_2 > MO_2')
    arcpy.CalculateField_management("Subset", "TG_3","max(0,!TG_2! + !DIFF_2!)","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "MO_3","!MO_2!","PYTHON_9.3")
    arcpy.CalculateField_management("Subset", "WAT_2","!WAT_1!","PYTHON_9.3")

    arcpy.SelectLayerByAttribute_management("Subset","CLEAR_SELECTION")

    print("--- Final #6: Field Adjustments Complete  %s seconds ---" % (time.time() - start_time))

def final_7(CoName, Temp10GDB, FinalGDB, FinalDirectory, WLT, WLF, Snap):
    start_time = time.time()
    arcpy.env.snapRaster = Snap
    arcpy.env.extent = Snap
    Combo = str(Temp10GDB) + "Combo"
    arcpy.MakeRasterLayer_management(str(Temp10GDB) + str(CoName) + "_Combo","Adjusted")
    arcpy.AddJoin_management("Adjusted","Value", Combo,"Value") #no need to save Combo as a DBF prior to this.
    P6classes = arcpy.sa.ExtractByMask("Adjusted","Adjusted") # Fooling ArcGIS to convert the Raster Layer to Raster Dataset (must include sa in the string).
    arcpy.Delete_management("in_memory")
    outRaster1 = Lookup(P6classes,"IR")
    outRaster1.save(str(FinalGDB) + str(CoName) + "_IR")
    outRaster2 = Lookup(P6classes, "INR_1")
    outRaster2.save(str(FinalGDB) + str(CoName) + "_INR")
    outRaster3 = Lookup(P6classes, "TCI")
    outRaster3.save(str(FinalGDB) + str(CoName) + "_TCI")
    outRaster4 = Lookup(P6classes,"WAT_2")
    outRaster4.save(str(FinalGDB) + str(CoName) + "_WAT")
    if arcpy.Exists(WLT):
        outRaster5 = Lookup(P6classes, "WLT_1")
        outRaster5.save(str(FinalGDB) + str(CoName) + "_WLT")
    if arcpy.Exists(WLF):
        outRaster6 = Lookup(P6classes, "WLF_1")
        outRaster6.save(str(FinalGDB) + str(CoName) + "_WLF")
    outRaster7 = Lookup(P6classes, "WLO_1")
    outRaster7.save(str(FinalGDB) + str(CoName) + "_WLO")
    outRaster8 = Lookup(P6classes, "FOR_1")
    outRaster8.save(str(FinalGDB) + str(CoName) + "_FOR")
    outRaster9 = Lookup(P6classes, "TCT_1")
    outRaster9.save(str(FinalGDB) + str(CoName) + "_TCT")
    outRaster10 = Lookup(P6classes, "MO_3")
    outRaster10.save(str(FinalGDB) + str(CoName) + "_MO")
    outRaster11 = Lookup(P6classes, "TG_3")
    outRaster11.save(str(FinalGDB) + str(CoName) + "_TG")
    outRaster12 = Lookup(P6classes, "CRP_2")
    outRaster12.save(str(FinalGDB) + str(CoName) + "_CRP")
    outRaster13 = Lookup(P6classes, "PAS_2")
    outRaster13.save(str(FinalGDB) + str(CoName) + "_PAS")
    arcpy.env.workspace = FinalGDB
    arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_IR",str(FinalDirectory) + str(CoName) + "_IR.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_INR",str(FinalDirectory) + str(CoName) + "_INR.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_TCI",str(FinalDirectory) + str(CoName) + "_TCI.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_WAT",str(FinalDirectory) + str(CoName) + "_WAT.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    if arcpy.Exists(WLT):
        arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_WLT",str(FinalDirectory) + str(CoName) + "_WLT.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    if arcpy.Exists(WLF):
        arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_WLF",str(FinalDirectory) + str(CoName) + "_WLF.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_WLO",str(FinalDirectory) + str(CoName) + "_WLO.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_FOR",str(FinalDirectory) + str(CoName) + "_FOR.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_TCT",str(FinalDirectory) + str(CoName) + "_TCT.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_MO",str(FinalDirectory) + str(CoName) + "_MO.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_TG",str(FinalDirectory) + str(CoName) + "_TG.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_CRP",str(FinalDirectory) + str(CoName) + "_CRP.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    arcpy.CopyRaster_management(str(FinalGDB) + str(CoName) + "_PAS",str(FinalDirectory) + str(CoName) + "_PAS.tif","","0","0","NONE","NONE","8_BIT_UNSIGNED","NONE","NONE","TIFF")
    print("--- Final #7: Final Phase 6 Rasters Complete  %s seconds ---" % (time.time() - start_time))

## #############################################################################
##  <<< MAIN >>>
##  Call each function here
## #############################################################################
def main():

    print('\n<<< Start >>>\r\n')
    ALL_start_time = time.time()
    #ALL_start_time = timeit.default_timer()

    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.AddMessage("Checking out Spatial")
        arcpy.CheckOutExtension("Spatial")
    else:
        arcpy.AddError("Unable to get spatial analyst extension")
        arcpy.AddMessage(arcpy.GetMessages(0))
        sys.exit(0)

    # Location of geodatabases
    if not arcpy.Exists("D:/B__P6_Analyst/A__P6_Temp"):
        arcpy.CreateFolder_management("D:/B__P6_Analyst","A__P6_Temp")
    MASKgdbDirectory = "D:/B__P6_Analyst/A__P6_Masks/" #Directory where MASK geodatabases are located
    LUgdbDirectory = "D:/B__P6_Analyst/A__P6_1mLU/"  #Directory where LAND USE geodatabases are located

    ### Do all the set up here, then call each funtion passing necessary variables ###
    # Loops through the mask directory, extracts file's basename and strips "_Mask.gdb" suffix to use as CoName
    env.workspace = MASKgdbDirectory
    for gdb in arcpy.ListWorkspaces("*"):
        gdb_basename = os.path.basename(gdb)
        gdb_ext = os.path.splitext(gdb_basename)[0]
        CoName = gdb_ext.rsplit('_',1)[0]
        print("'%s' ===>>> '%s'" % (gdb_basename, CoName))

        # Universal Global variables:
        CoGDB = os.path.join(str(MASKgdbDirectory),str(CoName) + "_Masks.gdb/")
        LuGDB = os.path.join(str(LUgdbDirectory),str(CoName) + "_1mLU.gdb/")
        arcpy.env.workspace = CoGDB
        arcpy.env.overwriteOutput = True
        coord_data = os.path.join("D:/B__P6_Analyst/A__P6_Temp/", str(CoName) + "_10m.gdb/", str(CoName) + "_Snap")
        arcpy.env.outputCoordinateSystem = arcpy.Describe(coord_data).spatialReference
        arcpy.env.workspace = CoGDB
        arcpy.env.extent = os.path.join(str(LuGDB) + str(CoName) + "_IR_1m")
        arcpy.env.parallelProcessingFactor = "100%"
        arcpy.env.snapRaster = str(LuGDB) + str(CoName) + "_IR_1m" #location of the snap raster

        # Local variables:
        BAR = os.path.join(str(CoGDB) + str(CoName) + "_Barren")
        BEACH = os.path.join(str(CoGDB) + str(CoGDB),str(CoName) + "_MOBeach")
        DEV113 = os.path.join(str(CoGDB) + str(CoName) + "_DEV113")
        DEV37 = os.path.join(str(CoGDB) + str(CoName) + "_DEV37")
        DEV27 = os.path.join(str(CoGDB) + str(CoName) + "_DEV27")
        DEV18 = os.path.join(str(CoGDB) + str(CoName) + "_DEV18")
        FEDS = os.path.join(str(CoGDB) + str(CoName) + "_FedPark")
        FINR_LU = os.path.join(str(CoGDB) + str(CoName) + "_FracINR")
        FTG_LU = os.path.join(str(CoGDB) + str(CoName) + "_FracTG")
        INST = os.path.join(str(CoGDB) + str(CoName) + "_TurfNT")
        T_LANDUSE = os.path.join(str(CoGDB) + str(CoName) + "_TgLU")
        M_LANDUSE = os.path.join(str(CoGDB) + str(CoName) + "_MoLU")
        LV = os.path.join(str(CoGDB) + str(CoName) + "_LV")
        MINE = os.path.join(str(CoGDB) + str(CoName) + "_ExtLFill")
        PARCELS = os.path.join(str(CoGDB) + str(CoName) + "_Parcels")
        ROW = os.path.join(str(CoGDB) + str(CoName) + "_RoW")
        SS = os.path.join(str(CoGDB),str(CoName) + "_SS")
        TC = os.path.join(str(CoGDB) + str(CoName) + "_TC")
        TREES = os.path.join(str(CoGDB) + str(CoName) + "_MOTrees")
        
        # 1 meter LU Rasters - Listed in Hierarchical Order:
        IR = os.path.join(str(LuGDB) + str(CoName) + "_IR_1m")
        INR = os.path.join(str(LuGDB) + str(CoName) + "_INR_1m")
        TCI = os.path.join(str(LuGDB) + str(CoName) + "_TCoI_1m")
        WAT = os.path.join(str(LuGDB) + str(CoName) + "_WAT_1m")
        WLT = os.path.join(str(LuGDB) + str(CoName) + "_WLT_1m")
        WLF = os.path.join(str(LuGDB) + str(CoName) + "_WLF_1m")
        WLO = os.path.join(str(LuGDB) + str(CoName) + "_WLO_1m")
        FOR = os.path.join(str(LuGDB) + str(CoName) + "_FOR_1m")
        TCT = os.path.join(str(LuGDB) + str(CoName) + "_TCT_1m")
        MO = os.path.join(str(LuGDB) + str(CoName) + "_MO_1m")
        FTG = os.path.join(str(LuGDB) + str(CoName) + "_FTG_1m")
        FINR = os.path.join(str(LuGDB) + str(CoName) + "_FINR_1m")
        TG = os.path.join(str(LuGDB) + str(CoName) + "_TG_1m")

        # Temp Masks
        RTmask = os.path.join(str(CoGDB) + str(CoName) + "_RTmask") 
        FTGMask = os.path.join(str(CoGDB) + str(CoName) + "_FTGmask")
        TGMask = os.path.join(str(CoGDB) + str(CoName) + "_TGmask")
        TURFparcels = os.path.join(str(CoGDB),str(CoName) + "_TURF_parcels")
        FTGparcels = os.path.join(str(CoGDB),str(CoName) + "_FTG_parcels")
        TURFtemp = os.path.join(str(CoGDB) + str(CoName) + "_TURFtemp")
        FTGtemp = os.path.join(str(CoGDB) + str(CoName) + "_FTGtemp")
        FINRtemp = os.path.join(str(CoGDB) + str(CoName) + "_FINRtemp")
        URBmask = os.path.join(str(CoGDB) + str(CoName) + "_URBmask")
        RURmask = os.path.join(str(CoGDB) + str(CoName) + "_RURmask")
        WAT_FOR = os.path.join(str(CoGDB),str(CoName) + "_watFOR")
        POT_FOR = os.path.join(str(CoGDB),str(CoName) + "_potFOR")
        RLTCP = os.path.join(str(CoGDB) + str(CoName) + "_RLTCP")
        EDGE = os.path.join(str(CoGDB) + str(CoName) + "_EDGE")
        CDEdge = os.path.join(str(CoGDB) + str(CoName) + "_EDGE")
        HERB = os.path.join(str(CoGDB) + str(CoName) + "_Herb")
        MOherb = os.path.join(str(CoGDB) + str(CoName) + "_MOherb")

        print ("IR", arcpy.Exists(IR))
        print ("INR", arcpy.Exists(INR))
        print ("TCI", arcpy.Exists(TCI))
        print("WAT", arcpy.Exists(WAT))
        print("BAR", arcpy.Exists(BAR))
        print("LV", arcpy.Exists(LV))
        print("SS", arcpy.Exists(SS))
        print("TC", arcpy.Exists(TC))
        print("BAR", arcpy.Exists(BAR))
        print("DEV113", arcpy.Exists(DEV113))
        print("DEV37", arcpy.Exists(DEV37))
        print("DEV27", arcpy.Exists(DEV27))
        print("DEV18", arcpy.Exists(DEV18))
        print("FEDS", arcpy.Exists(FEDS))
        print("BEACH", arcpy.Exists(BEACH))
        print("MINE", arcpy.Exists(MINE))
        print("T_LANDUSE", arcpy.Exists(T_LANDUSE))
        print("M_LANDUSE", arcpy.Exists(M_LANDUSE))
        print("FINR_LU", arcpy.Exists(FINR_LU))
        print("FTG_LU", arcpy.Exists(FTG_LU))
        print("INST", arcpy.Exists(INST))
        print("PARCELS", arcpy.Exists(PARCELS))
        print("ROW", arcpy.Exists(ROW))
        print ("TREES", arcpy.Exists(TREES))

        #Newly defined variables
        INRmask = os.path.join(str(CoGDB),str(CoName) + "_INRmask")
        
        #---------------------------TURF & FRACTIONAL MODELS--------------------------------
        #ALL_start_time = time.time()
        start_time = time.time()
        arcpy.Delete_management(str(CoGDB) + "Parcel_IMP")
        arcpy.Delete_management(str(CoGDB) + "Parcel_IMP2")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_INRmask")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_RTmask")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_Parcels_TURFtemp")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_Parcels_TURF")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_TURF_parcels")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_Parcels_FTGtemp")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_Parcels_FTG")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_FTG_parcels")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_TGmask")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_FTGmask")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_TURFtemp")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_FTGtemp")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_FINRtemp")
        arcpy.Delete_management(str(LuGDB) + str(CoName) + "_TG_1m")
        arcpy.Delete_management(str(LuGDB) + str(CoName) + "_TCI_1m")
        arcpy.Delete_management(str(LuGDB) + str(CoName) + "_FTG_1m")
        arcpy.Delete_management(str(LuGDB) + str(CoName) + "_FINR_1m")
        print("--- Removal of TURF & FRAC Duplicate Files Complete %s seconds ---" % (time.time() - start_time))

        ### End the set up section ###
        
        # Call each function, passing the necessary variables...
        turf_1(CoName, CoGDB, INR, IR, INRmask, TCI)

        turf_2(CoName, CoGDB, HERB, BAR, LV)

        turf_3(CoName, CoGDB, DEV18, DEV27)

        # # TURF 4: Create Parcel-based Turf and Fractional Turf Masks
        if arcpy.Exists(PARCELS):
            turf_4a(CoName, CoGDB, PARCELS, IR)

            turf_4b(CoName, CoGDB, PARCELS)

            turf_4c(CoName, CoGDB, PARCELS)

            turf_4d(CoName, CoGDB, DEV113, RTmask, ROW, INST, T_LANDUSE, TURFparcels)

            turf_4e(CoName, CoGDB, FTG_LU, FEDS, FTGparcels)

        else:
            turf_5a(CoName, CoGDB, DEV113, RTmask, ROW, INST, T_LANDUSE)

            turf_5b(CoName, CoGDB, FTG_LU, FEDS_sm)

        turf_6(CoName, CoGDB, LuGDB, HERB, TGMask, TURFtemp)

        frac_1(CoName, LuGDB, HERB, FTGMask, FTGtemp)

        frac_2(CoName, LuGDB, FINR, HERB, FINRtemp)

        # TURF & FRACTIONAL Clean up
        start_time = time.time()
        arcpy.Delete_management(str(CoGDB) + "Parcel_IMP")
        arcpy.Delete_management(str(CoGDB) + "Parcel_IMP2")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_RTmask")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_Parcels_TURFtemp")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_Parcels_TURF")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_TURF_parcels")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_Parcels_FTGtemp")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_Parcels_FTG")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_FTG_parcels")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_TGmask")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_FTGmask")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_TURFtemp")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_FTGtemp")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_FINRtemp")
        print("--- TURF & FRAC Clean Up Complete %s seconds ---" % (time.time() - start_time))

        #--------------------------------FOREST MODEL----------------------------------------
        start_time = time.time()
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_RLTCP")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_EDGE")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_CDEdge")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_URBmask")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_RURmask")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_CDEdge")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_URB_TCT")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_RUR_TCT")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_TCT1")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_nonTCT")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_potFOR")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_NATnhbrs")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_ForRG")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_MOtemp")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_MOspace")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_MOherb")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_MOTrees")
        arcpy.Delete_management(str(LuGDB) + str(CoName) + "_FOR_1m")
        arcpy.Delete_management(str(LuGDB) + str(CoName) + "_MO_1m")

        for_1(CoName, DEV113, TC)

        for_2(CoName, TC, DEV27)

        for_3(CoName, CoGDB, RLTCP, EDGE)

        for_4(CoName, DEV37, CDEdge)

        for_5(CoName, DEV18, TC)
        
        for_6(CoName, CoGDB, LuGDB)
        
        for_7(CoName, TCT, TC)
        
        ############################# WETLAND SUBMODEL #############################
        #Extract str(CoName) + "_WL" by each of the three masks mask
        #Mosaic these three rasters with the nwi rasters -prioritizing NWI

        # Wetland Model: Define input layers
		fc_Tidal = os.path.join(str(CoGDB), str(CoName) +"_mask_tidal")
		fc_FPlain = os.path.join(str(CoGDB), str(CoName) +"_mask_fplain")
		fc_OTHWL = os.path.join(str(CoGDB), str(CoName) +"_mask_oth_wl")
		nwi_Tidal = os.path.join(str(CoGDB), str(CoName) +"_Tidal")
		nwi_FPlain = os.path.join(str(CoGDB), str(CoName) +"_NTFPW")
		nwi_OTHWL = os.path.join(str(CoGDB), str(CoName) +"_OtherWL")
		cc_wetlands = os.path.join(str(CoGDB), str(CoName) +"_WL")
		pa_wetlands = os.path.join(str(CoGDB), str(CoName) +"_PA_wet")

        print ("Wetland Model Started")
        # Reclassification of CC Wetlands and Merge with NWI
        wl_start_time = time.time()
        if arcpy.Exists(cc_wetlands) and arcpy.Exists(pa_wetlands):
			input_rasters = cc_wetlands;pa_wetlands
			arcpy.MosaicToNewRaster_management (input_rasters, str(CoGDB), str(CoName) + "_ccpa", "", "4_BIT", "1", "1", "FIRST", "")
			ccpa_wetlands = os.path.join(str(CoGDB), str(CoName) +"_ccpa")
			
			wet_1_ccpa(CoName, CoGDB, LuGDB, fc_Tidal, ccpa_wetlands, nwi_Tidal)
			
			wet_2_ccpa(CoName, CoGDB, LuGDB, fc_FPlain, ccpa_wetlands, nwi_FPlain)
			
			wet_3_ccpa(CoName, CoGDB, LuGDB, fc_OTHWL, ccpa_wetlands, nwi_OTHWL)

		elif arcpy.Exists(cc_wetlands):
 			wet_1_cc(CoName, CoGDB, LuGDB, fc_Tidal, cc_wetlands, nwi_Tidal)
			
			wet_2_cc(CoName, CoGDB, LuGDB, fc_FPlain, cc_wetlands, nwi_FPlain)
			
			wet_3_cc(CoName, CoGDB, LuGDB, fc_OTHWL, cc_wetlands, nwi_OTHWL)
 
		elif arcpy.Exists(pa_wetlands):
			
			wet_1_pa(CoName, CoGDB, LuGDB, fc_Tidal, pa_wetlands, nwi_Tidal)
			
			wet_2_pa(CoName, CoGDB, LuGDB, fc_FPlain, pa_wetlands, nwi_FPlain)
			
			wet_3_pa(CoName, CoGDB, LuGDB, fc_OTHWL, pa_wetlands, nwi_OTHWL)

		else:
			
			if arcpy.Exists(nwi_Tidal):
				arcpy.CopyRaster_management(nwi_Tidal,str(LuGDB) + str(CoName)+ "_WLT_1m","","0","0","","","4_BIT")
			if arcpy.Exists(nwi_FPlain):
				WLFprep = Con(Raster(nwi_FPlain)==2,1)
				arcpy.CopyRaster_management(WLFprep,str(LuGDB) + str(CoName)+ "_WLF_1m","","0","0","","","4_BIT")
			if arcpy.Exists(nwi_OTHWL):
				WLOprep = Con(Raster(nwi_OTHWL)==3,1)
				arcpy.CopyRaster_management(WLOprep,str(LuGDB) + str(CoName)+ "_WLO_1m","","0","0","","","4_BIT")

		print("--- Wetland Model Complete %s seconds ---" % (time.time() - wl_start_time))
        ###########################################################################################################
        
        for_8(CoName, CoGDB, LuGDB, TC, WAT, WLF, WLO, WLT, WAT_FOR, POT_FOR)
        
        #---------------------------MIXED OPEN MODEL-----------------------------------------------------
        # MO 1: Create Mixed Open with just MOtrees and Scrub-shrub (no ancillary data)
		inrasListMO = [ ]
		if arcpy.Exists(BEACH):
			inrasListMO.append(BEACH)
		if arcpy.Exists(M_LANDUSE):
			inrasListMO.append(M_LANDUSE)
		if arcpy.Exists(MINE):
			inrasListMO.append(MINE)
		if arcpy.Exists(FEDS_lrg):
			inrasListMO.append(FEDS_lrg)

        if not inrasListMO:

            mo_1(CoName, CoGDB, LuGDB, TREES, SS)

        else:

            mo_2a(CoName, CoGDB, inrasListMO)

            mo_2b(CoName, CoGDB, BAR, LV)

            mo_2c(CoName, CoGDB, HERB, MOherb)

            mo_2d(CoName, CoGDB, LuGDB, MOherb, TREES, SS)

        # FOREST & MIXED OPEN Clean up
        start_time = time.time()
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_RLTCP")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_EDGE")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_CDEdge")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_URBmask")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_RURmask")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_CDEdge")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_URB_TCT")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_RUR_TCT")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_TCT1")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_nonTCT")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_potFOR")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_NATnhbrs")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_ForRG")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_MOtemp")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_MOspace")
        arcpy.Delete_management(str(CoGDB) + str(CoName) + "_MOherb")
        print("--- FOREST & MIXED OPEN Clean Up Complete %s seconds ---" % (time.time() - start_time))

        
        #----------------------FINAL AGGREGATION MODEL-----------------------------------------
        print ("IR", arcpy.Exists(IR))
        print ("INR", arcpy.Exists(INR))
        print ("TCI", arcpy.Exists(TCI))
        print ("WAT", arcpy.Exists(WAT))
        print ("WLT", arcpy.Exists(WLT))
        print ("WLF", arcpy.Exists(WLF))
        print ("WLO", arcpy.Exists(WLO))
        print ("FOR", arcpy.Exists(FOR))
        print ("TCT", arcpy.Exists(TCT))
        print ("MO", arcpy.Exists(MO))
        print ("FTG", arcpy.Exists(FTG))
        print ("FINR", arcpy.Exists(FINR))
        print ("TG", arcpy.Exists(TG))

        # Final 1: Prepare directory structures
        TempDirectory = "D:/B__P6_Analyst/A__P6_Temp/"
        if not arcpy.Exists(str(TempDirectory) + str(CoName) + "_1m.gdb"):
            arcpy.CreateFileGDB_management(str(TempDirectory), str(CoName) + "_1m.gdb")
        if not arcpy.Exists(str(TempDirectory) + str(CoName) + "_10m.gdb"):
            arcpy.CreateFileGDB_management(str(TempDirectory), str(CoName) + "_10m.gdb")
        TempGDB = os.path.join(str(TempDirectory) + str(CoName) + "_1m.gdb/")
        Temp10GDB = os.path.join(str(TempDirectory) + str(CoName) + "_10m.gdb/")
        arcpy.env.scratchWorkspace = TempGDB
        if not arcpy.Exists("D:/B__P6_Analyst/A__P6_10mLU"):
            arcpy.CreateFolder_management("D:/B__P6_Analyst","A__P6_10mLU")
        DirPath = "D:/B__P6_Analyst/A__P6_10mLU/"
        if not arcpy.Exists(str(DirPath) + str(CoName) + "_10m.gdb"):
            arcpy.CreateFileGDB_management(str(DirPath), str(CoName) + "_10m.gdb")
        FinalGDB = os.path.join(str(DirPath) + str(CoName) + "_10m.gdb/")
        if not arcpy.Exists("D:/B__P6_Analyst/" + str(CoName) + "_FINAL"):
            arcpy.CreateFolder_management("D:/B__P6_Analyst", str(CoName) + "_FINAL")
        FinalDirectory = "D:/B__P6_Analyst/" + str(CoName) + "_FINAL/"

        #Snap Raster
        Snap = os.path.join(str(Temp10GDB) + str(CoName) + "_Snap")
        
        final_2_3(CoName, CoGDB, IR, INR, TCI, WAT, WLT, WLF, WLO, FOR, TCT, MO, FTG, FINR, TG)
        
        final_4(CoName, CoGDB, LuGDB, TempGDB, Temp10GDB, TempDirectory, Snap)
        
        final_5(CoName, Temp10GDB, Snap)
        
        final_6(CoName, Temp10GDB, FINR, WLT, WLF, Snap)

        final_7(CoName, Temp10GDB, FinalGDB, FinalDirectory, WLT, WLF, Snap)

    print("--- All Models Complete %s seconds ---" % (time.time() - ALL_start_time))
## #############################################################################
##  <<< END MAIN >>>
## #############################################################################

# Need this to execute main()
if __name__ == "__main__":
    main()
