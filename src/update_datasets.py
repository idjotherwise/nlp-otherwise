import pandas as pd

"""
Script to update all the datasets, ran daily
"""


"""
Austria dataset
"""

new_timeline_data = pd.read_csv("../data_sets/CovidFaelle_Timeline.csv", sep=";")
new_timeline_data['Time'] = pd.to_datetime(new_timeline_data['Time'], format='%d.%m.%Y %H:%M:%S')
new_timeline_data['SiebenTageInzidenzFaelle'] = [float('.'.join(x.split(','))) for x in new_timeline_data.SiebenTageInzidenzFaelle]

new_tests_data = pd.read_csv("../data_sets/CovidFallzahlen.csv", sep=";")
new_tests_data['Time'] = pd.to_datetime(new_tests_data['Meldedat'], format='%d.%m.%Y')
new_tests_data = new_tests_data.drop(columns=['MeldeDatum', 'Bundesland', 'Meldedat'])

new_timeline_data_date = new_timeline_data.Time.iloc[-1]
new_tests_data_date = new_tests_data.Time.iloc[-1]

print("Test data from: ", new_tests_data_date)
print("Cases data from: ", new_timeline_data_date)

print("Starting preprocessing..")

new_tests_data['HospTakenPercent'] = 100 * new_tests_data.FZHosp / (new_tests_data.FZHosp + new_tests_data.FZHospFree)
new_tests_data['ICUTakenPercent'] = 100 * new_tests_data.FZICU / (new_tests_data.FZICU + new_tests_data.FZICUFree)

full_data = new_timeline_data.set_index(['Time', 'BundeslandID']).join(new_tests_data.set_index(['Time', 'BundeslandID'])).fillna(0).reset_index()

full_data['DailyTestGesamt'] = full_data.groupby(by='BundeslandID').TestGesamt.transform(lambda s: s.diff())
full_data['DailyTestGesamt'] = full_data.DailyTestGesamt.where(full_data.DailyTestGesamt > 0, 0)
full_data = full_data.sort_values(by=['Bundesland', 'Time']).reset_index(drop=True)
full_data['WeeklyTestGesamt'] = full_data.groupby(by=['Bundesland'])['DailyTestGesamt'].transform(lambda s: s.rolling(7, min_periods=1).sum())
full_data = full_data.sort_values(['Time', 'Bundesland']).reset_index(drop=True)

full_data['TestRate'] = full_data.TestGesamt / full_data.AnzEinwohner
full_data['NewTestRate'] = full_data.DailyTestGesamt / full_data.AnzEinwohner
full_data['WeeklyTestRate'] = full_data.WeeklyTestGesamt / full_data.AnzEinwohner

full_data['Positivity'] = 100 * full_data.AnzahlFaelle7Tage	/full_data.WeeklyTestGesamt

full_data['TwoWeeklyCases'] = full_data.groupby(by=['Bundesland'])['AnzahlFaelle'].transform(lambda s: s.rolling(14, min_periods=1).sum())
full_data['TwoWeeklyCasesRate'] = 100000*full_data['TwoWeeklyCases']/full_data.AnzEinwohner

new_timeline_data.to_csv("../data_sets/CovidFaelle_Timeline.csv", index=False)
new_tests_data.to_csv("../data_sets/CovidFallzahlen.csv", index=False)
full_data.to_csv("../data_sets/at_full_data.csv", index=False)
print("Successfully saved Austrian data.")

"""
European dataset
"""

print("Getting latest data from covid19dh")

from covid19dh import covid19
import datetime

countries = ["Italy", 
             "Austria",
             "Germany",
             "Belgium",
             "France",
             "United Kingdom",
             "Switzerland",
             "Portugal"
            ]

yesterday = datetime.date.today() - datetime.timedelta(days=1)

x, src = covid19(countries, raw=True, verbose=False, end=yesterday, cache=False)
print("Preprocessing european data..")
x_small = x.loc[:, ['administrative_area_level_1', 'date', 'vaccines', 'confirmed','tests', 'recovered', 'deaths', 'population']]
x_small.rename(columns={'administrative_area_level_1': 'id'}, inplace=True)

x_small['confirmed_per'] = 100000 * x_small['confirmed'] / x_small['population']
x_small['deaths_per'] = 100000 * x_small['deaths'] / x_small['population']
x_small['ratio'] = 100 * (x_small['deaths']) / (x_small['confirmed'])
x_small['tests_per'] = 100000 * (x_small['tests']) / (x_small['population'])
x_small['vaccines_per'] = x_small['vaccines'] / x_small['population']

x_small['new_cases']=x_small.groupby('id').confirmed.diff().fillna(0)
x_small['new_cases_per']=x_small.groupby('id').confirmed_per.diff().fillna(0)
x_small.to_csv("../data_sets/european_covid.csv", index=False)
print("Succesfully updated European data")