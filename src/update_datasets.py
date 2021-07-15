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
    new_tests_data['HospTakenPercent'] = 100 * new_tests_data.FZHosp / (new_tests_data.FZHosp + new_tests_data.FZHospFree)
    new_tests_data['ICUTakenPercent'] = 100 * new_tests_data.FZICU / (new_tests_data.FZICU + new_tests_data.FZICUFree)

    full_data = new_timeline_data.set_index(['Time', 'BundeslandID']).join(new_tests_data.set_index(['Time', 'BundeslandID'])).fillna(0).reset_index()

    full_data['DailyTestGesamt']=full_data.groupby(by='BundeslandID').TestGesamt.transform(lambda s: s.diff())
    full_data['DailyTestGesamt']=full_data.DailyTestGesamt.where(full_data.DailyTestGesamt > 0, 0)
    full_data=full_data.sort_values(by=['Bundesland','Time']).reset_index(drop=True)
    full_data['WeeklyTestGesamt'] = full_data.groupby(by=['Bundesland'])['DailyTestGesamt'].transform(lambda s: s.rolling(7, min_periods=1).sum())
    full_data = full_data.sort_values(['Time', 'Bundesland']).reset_index(drop=True)

    full_data['TestRate'] = full_data.TestGesamt / full_data.AnzEinwohner
    full_data['NewTestRate'] = full_data.DailyTestGesamt / full_data.AnzEinwohner
    full_data['WeeklyTestRate'] = full_data.WeeklyTestGesamt / full_data.AnzEinwohner

    full_data['Positivity'] = 100 * full_data.AnzahlFaelle7Tage	/full_data.WeeklyTestGesamt

    full_data['TwoWeeklyCases']=full_data.groupby(by=['Bundesland'])['AnzahlFaelle'].transform(lambda s: s.rolling(14, min_periods=1).sum())
    full_data['TwoWeeklyCasesRate']=100000*full_data['TwoWeeklyCases']/full_data.AnzEinwohner
    
    new_timeline_data.to_csv("../data_sets/CovidFaelle_Timeline.csv", index=False)
    new_tests_data.to_csv("../data_sets/CovidFallzahlen.csv", index=False)
    full_data.to_csv("../data_sets/at_full_data.csv", index=False)
    print("Successfully saved data.")
