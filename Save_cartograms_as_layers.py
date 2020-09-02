import osgeo.ogr,os
dirpath = 'C:\\Users\\kevin\\Desktop\\COVID_MAP\\COVID-Cartograms\\'
folder_path_extension = 'Outputs\\Cartogram_layer_exports\\'

if os.path.exists (dirpath + folder_path_extension) == False:
   print('Path does not exist')
else:
    for vLayer in iface.mapCanvas().layers(): #For each layer, save as a geopackage
        if vLayer.type()==0: #Save only shapefiles
            QgsVectorFileWriter.writeAsVectorFormat(vLayer, dirpath + folder_path_extension + vLayer.name() + '.gpkg', 'utf-8',)
            print(vLayer.name() + ' saved successfully')