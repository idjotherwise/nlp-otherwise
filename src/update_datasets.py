import pandas as pd

try:
    current_timeline_data = pd.read_csv("../data_sets/CovidFaelle_Timeline.csv")
    current_timeline_data['Time'] = pd.to_datetime(current_timeline_data['Time'], format='%Y-%m-%d %H:%M:%S')
    current_tests_data = pd.read_csv("../data_sets/CovidFallzahlen.csv")
    current_tests_data['Time'] = pd.to_datetime(current_tests_data['Time'], format='%Y-%m-%d %H:%M:%S')

except:
    current_timeline_data = pd.DataFrame.from_dict({'Time' : ['2020-01-01 00:00:00']}, orient='columns')
    current_timeline_data['Time'] = pd.to_datetime(current_timeline_data['Time'], format='%Y-%m-%d %H:%M:%S')
    current_tests_data = pd.DataFrame.from_dict({'Time': ['2020-01-01 00:00:00']}, orient='columns')
    current_tests_data['Time'] = pd.to_datetime(current_tests_data['Time'], format='%Y-%m-%d %H:%M:%S')
    print("No local files found. Need to get it remotely.")


new_timeline_data = pd.read_csv("https://covid19-dashboard.ages.at/data/CovidFaelle_Timeline.csv", sep=';')
new_timeline_data['Time'] = pd.to_datetime(new_timeline_data['Time'], format='%d.%m.%Y %H:%M:%S')
new_timeline_data['SiebenTageInzidenzFaelle'] = [float('.'.join(x.split(','))) for x in new_timeline_data.SiebenTageInzidenzFaelle]

new_tests_data = pd.read_csv("https://covid19-dashboard.ages.at/data/CovidFallzahlen.csv", sep=';')
new_tests_data['Time'] = pd.to_datetime(new_tests_data['Meldedat'], format='%d.%m.%Y')
new_tests_data = new_tests_data.drop(columns=['MeldeDatum', 'Bundesland', 'Meldedat'])


current_timeline_latest_date = current_timeline_data.Time.iloc[-1]
current_tests_latest_date = current_tests_data.Time.iloc[-1]
new_timeline_data_date = new_timeline_data.Time.iloc[-1]
new_tests_data_date = new_tests_data.Time.iloc[-1]

print(current_timeline_latest_date)
print(new_tests_data_date)

up_to_date = current_timeline_latest_date == new_tests_data_date

if up_to_date:
    print("Already up to date. Doing nothing.")
else:
    print("Data out of date. Updating data files.")
    new_timeline_data.to_csv("../data_sets/CovidFaelle_Timeline.csv", index=False)
    new_tests_data.to_csv("../data_sets/CovidFallzahlen.csv", index=False)
    print("Successfully saved data.")
