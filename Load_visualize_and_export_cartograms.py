#Get refrence to project
from datetime import datetime
project = QgsProject.instance()
dirpath = 'C:\\Users\\kevin\\Desktop\\COVID_MAP\\COVID-Cartograms\\'
cartogram_data_dir = dirpath + 'Outputs\\Cartogram_layer_exports\\'

def calculate_deaths(date):
    column_name = date + '_' + date + '_Deaths'
    death_counts = []
    for feature in cartogram.getFeatures():
        death_counts.append(feature[column_name])
    return sum(death_counts)


for filename in os.listdir(cartogram_data_dir): #For each geopackge in the Cartogram export folder
    if filename.endswith(".gpkg"):
        date_formatted = filename[10:20]

        # Load cartogram in
        cartogram =  QgsVectorLayer(cartogram_data_dir + filename + '|layername=' + filename[:-5], date_formatted + '_Cartogram', 'ogr') 
        if not cartogram.isValid():
            print('Layer failed to load!', file=log)
        else:
            project.addMapLayer(cartogram)


        #Symbolizing the cartogram based on week over week increase in deaths
        symbolizedColumn = date_formatted + '_' + date_formatted + '_WoWPCTIncrease'

        myRangeList = []
        WoWPctDeaths = []
        for feature in cartogram.getFeatures():
            WoWPctDeaths.append(feature[symbolizedColumn])
        WoWPctDeaths.append(2147483647) # append max value to make an even 50 values for the loop
        WoWPctDeaths.sort()

        # Makes 10 quintiles based on week over week increase in deaths. The better a state is doing the lighter the red it is filled with
        for i in range(10):
            symbol = QgsSymbol.defaultSymbol(cartogram.geometryType())
            symbol.setColor(QColor(255, 255 - ((255 / 10) * i), 255 - ((255 / 10) * i)))      
            if i == 0:
                symbol_name = 'Low weekly \% increase in deaths'
            elif i == 9:
                symbol_name = 'High weekly \% increase in deaths'
            else:
                symbol_name = ''
            myRange = QgsRendererRange(WoWPctDeaths[i * 5], WoWPctDeaths[(i * 5) + 4], symbol, symbol_name)  
            myRangeList.append(myRange)

        myRenderer = QgsGraduatedSymbolRenderer(symbolizedColumn, myRangeList)  
        myRenderer.setMode(QgsGraduatedSymbolRenderer.Custom)               
        cartogram.setRenderer(myRenderer)


        #Create map layout to export
        manager = project.layoutManager()
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName(date_formatted)
        manager.addLayout(layout)

        #Put map on layout
        itemMap = QgsLayoutItemMap.create(layout)
        itemMap.attemptMove(QgsLayoutPoint(20, 20, QgsUnitTypes.LayoutMillimeters))
        itemMap.attemptResize(QgsLayoutSize(260, 180, QgsUnitTypes.LayoutMillimeters))
        rectangle = QgsRectangle(-2600000,-1800000,2600000,1800000)
        itemMap.setExtent(rectangle)
        itemMap.setCrs(QgsCoordinateReferenceSystem("ESRI:102003"))
        layout.addLayoutItem(itemMap) 

        #Put legend image on layout
        legend_image = QgsLayoutItemPicture(layout)
        legend_image.setPicturePath(dirpath + 'Map_Elements\\Scale.png')
        legend_image.attemptMove(QgsLayoutPoint(20, 190, QgsUnitTypes.LayoutMillimeters))
        legend_image.attemptResize(QgsLayoutSize(260, 20,QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(legend_image)

        #Put title layout, with date and total deaths
        title_date = datetime.strptime(date_formatted, '%Y-%m-%d').strftime('%d %B %Y')
        if(str(title_date)[0] == "0"):
            title_date = title_date[1:]
        total_deaths_lower49 = int(calculate_deaths(date_formatted))

        title = QgsLayoutItemLabel(layout)
        title.setFont(QFont('Arial', 28))
        title.attemptMove(QgsLayoutPoint(95, 10, QgsUnitTypes.LayoutMillimeters))
        title.attemptResize(QgsLayoutSize(260, 20,QgsUnitTypes.LayoutMillimeters))
        title.setText(title_date + ' - ' + f"{total_deaths_lower49:,d}" + ' deaths')
        layout.addLayoutItem(title)

        #Export as image
        export_layout = QgsProject.instance().layoutManager().layoutByName(date_formatted)
        export = QgsLayoutExporter(export_layout)
        worked = export.exportToImage(dirpath + 'Outputs\\Map_photos_exports\\' + export_layout.name() + '.jpg', QgsLayoutExporter.ImageExportSettings())
        print(f'Sucessfully exported ' + date_formatted)
