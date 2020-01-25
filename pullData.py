import webbrowser
import os
import pprint
import csv
import re
import pickle
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import datetime
import numpy as np
import pandas as pd

def pullHourlyDataLondon():
    for intYr in range(2010,2019+1):
        for intMnt in range(1,12+1):
            strQuery = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=10999&Year=' + str(intYr) + '&Month=' + str(intMnt) +'&timeframe=1&submit=Download+Data'
            tmp = webbrowser.open_new_tab(strQuery)
            
def sortCSVDataChronologically():
    data = {}
    directory = os.fsencode(os.getcwd()+'/WeatherData')
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        year = filename.split('-')[1].split('.')[0]
        month = filename.split('-')[0]
        if filename.endswith(".csv"):
            if year in data: 
                data[year][month] = os.getcwd()+'\WeatherData\\'+filename
            else:
                data[year] = {}
                data[year][month] = os.getcwd()+'\WeatherData\\'+filename
            continue
        else:
            continue
    return data
    
def pullCSVData(filename):
    with open(filename, newline='', encoding='UTF-8') as csvfile:
        data = list(csv.reader(csvfile))
    return data

def writeToCSV(dictionary_to_output, file_name):
    csv_file = file_name + ".csv"
    w = csv.writer(open(csv_file, "w"))
    for key, val in dictionary.items():
        w.writerow([key, val])

def cleanTwitterData(twitterData):
    cleanTwitterData = []
    for data in twitterData:
        if 'basketball' in data[6].lower() or 'volleyball' in data[6].lower() or 'badminton' in data[6].lower():
            tmp = [data[2],data[6].lower()]
            cleanTwitterData.append(tmp)
    tweet_dictionary = {}
    for data in cleanTwitterData:
        if data[0] not in tweet_dictionary:
            tweet_dictionary[data[0]] = {}
        for sport in ['basketball','volleyball','badminton']:
            if sport in data[1]:
                tweet_dictionary[data[0]][sport] = data[1].split(sport)[1][:3]
            
    for tweet in tweet_dictionary.keys():
        for sport in ['basketball','volleyball','badminton']:
            if sport not in tweet_dictionary[tweet]:
                tweet_dictionary[tweet][sport] = '0'
            tweet_dictionary[tweet][sport] = re.sub('[^0-9]','', tweet_dictionary[tweet][sport])

    with open('sport_data.pickle', 'wb') as handle:
        pickle.dump(tweet_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    return tweet_dictionary


def getTwitterData():
    infile = open('sport_data.pickle','rb')
    new_dict = pickle.load(infile)
    infile.close()
    return new_dict

def plotGraph(tweet_dictionary):
    time = [] 
    basketball = [] 
    volleyball = [] 
    badminton = []
    for key in tweet_dictionary:
        if tweet_dictionary[key]['basketball'] == '':
            tweet_dictionary[key]['basketball'] = 0
        if tweet_dictionary[key]['badminton'] == '':
            tweet_dictionary[key]['badminton'] = 0
        if tweet_dictionary[key]['volleyball'] == '':
            tweet_dictionary[key]['volleyball'] = 0
        time.append(datetime.datetime.strptime(key,'%Y-%m-%d %H:%M:%S'))
        basketball.append(int(tweet_dictionary[key]['basketball']))
        volleyball.append(int(tweet_dictionary[key]['volleyball']))
        badminton.append(int(tweet_dictionary[key]['badminton']))

    ax = plt.subplot(111)
    ax.bar(time, badminton, width=0.5, color='b', align='center')
    ax.bar(time, basketball, width=0.5, color='g', align='center')
    ax.bar(time, volleyball, width=0.5, color='r', align='center')
    ax.xaxis_date()

    plt.show()

def createDataSet(year):
    dataset = []
    for i in year:
        csvFile = pullCSVData(year[i])
        dataset.append(csvFile[1:])
    return dataset

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

def removeEmpty(dirty):
    data = []
    e = IndexError()
    for d in dirty:
        for l in range(len(d)-1):
            try:
                data.append(d[l][4:10] + [d[l][11],d[l][13],d[l][21]])
            except IndexError:
                continue
    return data

def tweetTimeToHour(tweets):
    new_dictionary = {}
    for key, value in tweets.items():
        tmp = str(datetime.datetime.strptime(key, '%Y-%m-%d %H:%M:%S').replace(microsecond=0,second=0,minute=0))
        new_dictionary[tmp] = tweets[key]
    return new_dictionary



if __name__ == "__main__":
    # twitterData = pullCSVData('twitter-recCentre.csv')
    tmp = sortCSVDataChronologically()
    weather_2017 = createDataSet(tmp['2017'])
    weather_2017 = removeEmpty(weather_2017)
    weather_2018 = createDataSet(tmp['2018'])
    weather_2018 = removeEmpty(weather_2018)
    weather_2019 = createDataSet(tmp['2019'])
    weather_2019 = removeEmpty(weather_2019)

    weather_headers = ["Date/Time","Year","Month","Day","Time","Temp (°C)","Dew Point Temp (°C)","Rel Hum (%)","Stn Press (kPa)"]
    
    
    twitterData = getTwitterData()
    twitterData = tweetTimeToHour(twitterData)
    tmp_new_weather = []
    for w in weather_2017:
        if w[2] in ['10','11','12']:
            tmp_new_weather.append(w)
    tmp_new_weather.reverse()
    weather_2017 = tmp_new_weather
    tmp_new_weather = []
    for w in weather_2018:
        tmp_new_weather.append(w)
    tmp_new_weather.reverse()
    weather_2018 = tmp_new_weather
    tmp_new_weather = []
    for w in weather_2019:
        tmp_new_weather.append(w)
    tmp_new_weather.reverse()
    weather_2019 = tmp_new_weather
    tmp_new_weather = []
    for key, value in twitterData.items():
        twitterData[key]['weather'] = [0,0,0,0,0,0,0,0,0,0]
        tweet_time = key.split(' ')[1].split(':')[0].strip()
        tweet_day = key.split('-')[2].split(' ')[0].strip()
        tweet_month = key.split('-')[1].split(' ')[0].strip()
        tweet_year = key[:4]
        if tweet_year == '2017':
            for w in weather_2017:
                if (tweet_month == w[2]):
                    if(tweet_day == w[3]):
                        if(int(tweet_time) == int(w[4].split(':')[0])):
                            twitterData[key]['weather'] = (w) 
        if tweet_year == '2018':
            for w in weather_2018:
                if (tweet_month == w[2]):
                    if(tweet_day == w[3]):
                        if(int(tweet_time) == int(w[4].split(':')[0])):
                            twitterData[key]['weather'] = (w)  
        if tweet_year == '2019':
            for w in weather_2019:
                if (tweet_month == w[2]):
                    if(tweet_day == w[3]):
                        if(int(tweet_time) == int(w[4].split(':')[0])):
                            twitterData[key]['weather'] = (w)
        
    
    headers = "#badminton #basketball #volleyball #temp #dewpoint #humidity #pressure #year #month #day #hour"
    print(headers)
    training_data = []
    for key, value in twitterData.items():
        if (value['weather']) != [0,0,0,0,0,0,0,0,0,0]:
            training_data.append([
                safe_cast(value['badminton'],int,0),
                safe_cast(value['basketball'],int,0),
                safe_cast(value['volleyball'],int,0), 
                safe_cast(value['weather'][5],float,0), 
                safe_cast(value['weather'][6],float,0), 
                safe_cast(value['weather'][7],float,0.5), 
                safe_cast(value['weather'][1],int), 
                safe_cast(value['weather'][2],int), 
                safe_cast(value['weather'][3],int), 
                safe_cast(str(value['weather'][4])[:2],int)])


    data = pd.DataFrame(training_data)
    data.columns = ["badminton","basketball", "volleyball", "temp", "dewpoint", "humidity","year", "month", "day", "hour"]
    data = data[data.hour != 0]
    data = data[data.hour != 1]
    data = data[data.hour != 2]
    data = data[data.hour != 3]
    data = data[data.hour != 4]
    data = data[data.hour != 5]
    
    with open('training_data.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(len(data))
    a = np.array(training_data)
    np.savetxt("training_data.csv", a, delimiter=",")


        


    
