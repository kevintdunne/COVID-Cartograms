from datetime import datetime

def calculate_deaths(date):
    column_name = date + '_' + date + '_Deaths'
    death_counts = []
    number_of_ones = 0
    for feature in cartogram.getFeatures():
        death_counts.append(feature[column_name])
        if feature[column_name] == 0.1:
            number_of_ones = number_of_ones + 1
    return int(sum(death_counts) - (number_of_ones * 0.1))

dirpath = 'C:\\Users\\kevin\\Desktop\\COVID_MAP\\COVID-Cartograms\\'
cartogram_data_dir = dirpath + 'Outputs\\Cartogram_layer_exports\\'

project = QgsProject.instance()



start_date_int = 0 # yyyymmdd format, 0 for all days
end_date_int = 99999999999999 # yyyymmdd format, 9999999999 for all days

for filename in os.listdir(cartogram_data_dir): #For each geopackge in the Cartogram export folder
    date_formatted = filename[10:20]
    filename_as_int = int(str(date_formatted[0:4] + date_formatted[5:7] + date_formatted[8:10])) 
    
    if filename.endswith(".gpkg") and filename_as_int >= start_date_int and filename_as_int <= end_date_int:
        date_formatted = filename[10:20]

        # Load cartogram later
        cartogram =  QgsVectorLayer(cartogram_data_dir + filename + '|layername=' + filename[:-5], date_formatted + '_Cartogram', 'ogr') 
        if not cartogram.isValid():
            print('Layer failed to load!', file=log)
        else:
            project.addMapLayer(cartogram)



        #Symbolize based on week over week increase in deaths
        # symbolizedColumn = date_formatted + '_' + date_formatted + '_WoWPCTIncrease'

        # myRangeList = []
        # WoWPctDeaths = []
        # for feature in cartogram.getFeatures():
        #     WoWPctDeaths.append(feature[symbolizedColumn])
        # WoWPctDeaths.append(2147483647) # append max value to make an even 50 values for the loop
        # WoWPctDeaths.sort()

        # # Makes 10 quintiles based on week over week increase in deaths. The better a state is doing the lighter the red it is filled with
        # for i in range(10):
        #     symbol = QgsSymbol.defaultSymbol(cartogram.geometryType())
        #     symbol.setColor(QColor(255, 255 - ((255 / 10) * i), 255 - ((255 / 10) * i)))      
        #     if i == 0:
        #         symbol_name = 'Low weekly \% increase in deaths'
        #     elif i == 9:
        #         symbol_name = 'High weekly \% increase in deaths'
        #     else:
        #         symbol_name = ''
        #     myRange = QgsRendererRange(WoWPctDeaths[i * 5], WoWPctDeaths[(i * 5) + 4], symbol, symbol_name)  
        #     myRangeList.append(myRange)

        # myRenderer = QgsGraduatedSymbolRenderer(symbolizedColumn, myRangeList)  
        # myRenderer.setMode(QgsGraduatedSymbolRenderer.Custom)               
        # cartogram.setRenderer(myRenderer)





        # Symbolize based on deaths per capita
        current_layer = iface.activeLayer()
        column_name = 'Deaths_per_thousand' + date_formatted

        # Create field for deaths per captia
        prov = current_layer.dataProvider()
        fld = QgsField(column_name, QVariant.Double)
        prov.addAttributes([fld])
        current_layer.updateFields()
        idx = current_layer.fields().lookupField(column_name)
        current_layer.startEditing()

        deaths_field_name = date_formatted + '_' + date_formatted + '_Deaths'
        expression = '"' + deaths_field_name + '"' + ' / (Population / 1000)'

        e = QgsExpression(expression)
        c = QgsExpressionContext()
        s = QgsExpressionContextScope()
        s.setFields(current_layer.fields())
        c.appendScope(s)
        e.prepare(c)

        # Calculate deaths per capita
        for f in current_layer.getFeatures():
            c.setFeature(f)
            value = e.evaluate(c)
            atts = {idx: value}
            current_layer.dataProvider().changeAttributeValues({f.id():atts})
        current_layer.commitChanges()

        myRangeList = []
        break_values = [0, .2, .4, .6, .8, 1, 1.2, 1.4, 1.6, 1000000000]
        number_categories = len(break_values) - 1

        # Create categories based on break_values arry
        for i in range(number_categories):
            symbol = QgsSymbol.defaultSymbol(cartogram.geometryType())
            symbol.setColor(QColor(255, 255 - ((255 / number_categories) * i), 255 - ((255 / number_categories) * i)))

            symbol_name = str(break_values[i]) + ' - ' + str(break_values[i + 1])
            myRange = QgsRendererRange(break_values[i], break_values[i + 1], symbol, symbol_name)  
            myRangeList.append(myRange)

        myRenderer = QgsGraduatedSymbolRenderer(column_name, myRangeList)  
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
        itemMap.attemptMove(QgsLayoutPoint(0, 0, QgsUnitTypes.LayoutMillimeters))
        itemMap.attemptResize(QgsLayoutSize(300, 300, QgsUnitTypes.LayoutMillimeters))
        rectangle = QgsRectangle(-3000000,-2100000,3000000,2200000)
        itemMap.setExtent(rectangle)
        itemMap.setCrs(QgsCoordinateReferenceSystem("ESRI:102003"))
        itemMap.setBackgroundColor(QtCore.Qt.black)
        layout.addLayoutItem(itemMap) 

        #Put legend image on layout
        legend_image = QgsLayoutItemPicture(layout)
        legend_image.setPicturePath(dirpath + 'Map_Elements\\Scale.png')
        legend_image.attemptMove(QgsLayoutPoint(20, 190, QgsUnitTypes.LayoutMillimeters))
        legend_image.attemptResize(QgsLayoutSize(260, 20,QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(legend_image)

        title_date = datetime.strptime(date_formatted, '%Y-%m-%d').strftime('%d %B %Y')
        total_deaths_lower49 = int(calculate_deaths(date_formatted))

        #Date
        title = QgsLayoutItemLabel(layout)
        title.setFont(QFont('Courier New Bold', 25))
        title.setFontColor(QtCore.Qt.white)
        title.attemptMove(QgsLayoutPoint(20, 10, QgsUnitTypes.LayoutMillimeters))
        title.attemptResize(QgsLayoutSize(100, 20,QgsUnitTypes.LayoutMillimeters))
        title.setText(title_date)
        layout.addLayoutItem(title)

        #Num of deaths
        title = QgsLayoutItemLabel(layout)
        title.setFont(QFont('Courier New Bold', 25))
        title.setFontColor(QtCore.Qt.white)
        title.attemptMove(QgsLayoutPoint(200, 10, QgsUnitTypes.LayoutMillimeters))
        title.attemptResize(QgsLayoutSize(100, 20,QgsUnitTypes.LayoutMillimeters))
        title.setText(f"{total_deaths_lower49:,d}" + ' deaths')
        layout.addLayoutItem(title)

        #Export as image
        export_layout = QgsProject.instance().layoutManager().layoutByName(date_formatted)
        export = QgsLayoutExporter(export_layout)
        worked = export.exportToImage(dirpath + 'Outputs\\Map_photos_exports\\' + export_layout.name() + '.jpg', QgsLayoutExporter.ImageExportSettings())
        print(f'Sucessfully exported ' + date_formatted)
        
        # Delete the made field for deaths per 100 population
        # ONLY if you are symbolizing based on deaths per capita
        caps = current_layer.dataProvider().capabilities()
        if caps and QgsVectorDataProvider.DeleteAttributes:
            res = current_layer.dataProvider().deleteAttributes([13])
            current_layer.updateFields()

        project.removeAllMapLayers()
