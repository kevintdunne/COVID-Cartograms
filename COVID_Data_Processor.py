import pandas, numpy
from datetime import datetime
dirpath = 'C:\\Users\\kevin\\Desktop\\COVID_MAP\\Real_Folder\\'

# Read raw COVID Tracking Project Data
# Data downloaded from https://covidtracking.com/data/download, the 'data for all state link'
# Directly downloadable at https://covidtracking.com/data/download/all-states-history.csv
df = pandas.read_csv(dirpath + '\\Raw_COVID_Data\\all-states-history-aug-26.csv')

#Clean data by dropping unneeded columns, data before March 12th 2020, juristictions outside the lower 49, filling NaN death values with 0, and sorting by date and state
df = df[['date','state','death']]
df = df[df.date >= 20200312]
df = df.drop(df[df.state.isin(['MP','PR','HI','GU','VI','AS','AK'])].index)
df['death'] = df['death'].fillna(0)
df.sort_values(['date', 'state'], ascending=[True, True], inplace=True)

num_input_rows = len(df.index)
num_columns = int((num_input_rows / 49) * 4)
one_row_per_state = pandas.DataFrame(index=range(49), columns=range(num_columns)) #Create intermediate dataframe. One row per state, with 4 columns per day of data

for i in range(num_input_rows):
    proper_row = i % 49 #All rows with same remainder of 49 will corrospond to the same state
    proper_column = (i // 49) * 4

    #date
    date_formatted = datetime.strptime(str(df.iloc[i, 0]),'%Y%m%d').strftime('%Y-%m-%d')
    one_row_per_state.at[proper_row, proper_column] = date_formatted

    #state abbrevation
    one_row_per_state.at[proper_row, proper_column + 1] = df.iloc[i, 1]

    #deaths
    one_row_per_state.at[proper_row, proper_column + 2] = df.iloc[i, 2]

    #weekly growth in Deaths
    deaths_today = one_row_per_state.iloc[proper_row, proper_column + 2] #pulling deaths today from line above
    deaths_week_ago = one_row_per_state.iloc[proper_row, proper_column - 28 + 2] #Need to go 7 days (28 columns) back. But -28 lands on the date column from 7 days ago, add 2 to get to death column for 7 days ago

    if proper_column < 28 or deaths_week_ago == 0: #first 28 columns are week of March 12th to 19th. No data from previous week, so set Weekly Death increase to zero
        one_row_per_state.at[proper_row, proper_column + 3] = 0
    else :#calculate pct change in deaths from today to last week
    	one_row_per_state.at[proper_row, proper_column + 3] = round(((deaths_today - deaths_week_ago) / deaths_week_ago) * 100, 2)


# Construct column headers for one_row_per_state
header = []
for j in range(num_columns):
	if j % 4 == 0:
		header.append('Date')
	elif j % 4 == 1:
		header.append('State')
	elif j % 4 == 2:
		header.append(one_row_per_state.iloc[1, j - 2] + '_Deaths')
	elif j % 4 == 3:
		header.append(one_row_per_state.iloc[1, j - 3] + '_WoWPCTIncrease')

one_row_per_state.columns = header


# Split one_row_per_state into a a csv file for each day, and export with appropriate name, and accompnying .csvt file
for j in range(int(num_columns / 4)):
	output = one_row_per_state.iloc[:, [j * 4, (j * 4) + 1, (j * 4) + 2, (j * 4) + 3]] #Each 4 rows are the data for a certian day
	date_as_string = str(output.iloc[0,0])

	file_name = dirpath + '\\Outputs\\Daily_COVID_data_exports\\' + date_as_string + '.csv'
	output.to_csv(file_name, index=False)

	csvt = open(file_name + 't', "w") #make csvt files so QGIS's delimted text import interprets the columns as the proper data types
	print('String(20),String(20),Integer64(10),Real(10)', file=csvt)
	csvt.close()

print(str(j) + ' CSV files exported sucessfully')