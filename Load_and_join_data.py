import os

#Clear Project
QgsProject.instance().removeAllMapLayers()
dirpath = 'C:\\Users\\kevin\\Desktop\\COVID_MAP\\COVID-Cartograms\\'


#Load US states layer
lower49_path = dirpath + 'Lower_49_Layer\\Lower_49.gpkg|layername=Lower_49'


#Load all CSVs within desired date range
start_date_int = 20200501 # yyyymmdd format, 0 for all days
end_date_int = 20200502 # yyyymmdd format, 9999999999 for all days
pct_layers_use = 1 # percentage of layers to load, in demoninator form. 1 processes all csvs, 2 loads 50%(every other day), 3 loads 33%(every 3rd day), etc.
COVID_data_dir = dirpath + '\\Outputs\\Daily_COVID_data_exports\\'

for filename in os.listdir(COVID_data_dir):
    filename_as_int = int(str(filename[0:4] + filename[5:7] + filename[8:10])) 

    if filename.endswith(".csv") and filename_as_int >= start_date_int and filename_as_int <= end_date_int and filename_as_int % pct_layers_use == 0: #For CSV's in the desired date range

        csv = QgsVectorLayer(COVID_data_dir + filename, filename[:-4], 'delimitedtext') # filename[:-4] gives date in yyyy-mm-dd, which is what we want to name the layer
        if not csv.isValid():
            print('Layer failed to load!')
        else:
            QgsProject.instance().addMapLayer(csv) # Loads each csv into QGIS

        lower49 =  QgsVectorLayer(lower49_path, filename[:-4], 'ogr') # filename[:-4] gives date in yyyy-mm-dd, which is what we want to name the layer
        if not lower49.isValid():
            print('Layer failed to load!')
        else:
            QgsProject.instance().addMapLayer(lower49) # For each loaded csv, Loads a copy of lower49 shapefile into QGIS

        joinObject = QgsVectorLayerJoinInfo()
        joinObject.setJoinFieldName('State')
        joinObject.setTargetFieldName('STUSPS')
        joinObject.setJoinLayer(csv)
        lower49.addJoin(joinObject) #Joins each CSV to its respective shapefile based on state Abbrevation


# # Make Cartogram dialogue
# import cartogram3
# from cartogram3 import *

# cart = cartogram3.Cartogram(iface)
# cartogram3.Cartogram.run(cart)