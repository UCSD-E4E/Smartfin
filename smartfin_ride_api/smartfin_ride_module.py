import pandas as pd
import numpy as np

import os
import datetime
import pytz
import re
import requests
import netCDF4
import datetime
import time
from bs4 import BeautifulSoup
import json
import sys
import random

from io import StringIO

from double_integral_bandpass import double_integral_bandpass_filter


# 14743 - Motion Control July 10th
# 14750 - Magnetometer Control July 11th
# 14814 - Pool Displacement Control July 17th
# 14815 - Compass Orientation (Lying on Charger Side) July 19th
# 14816 - Orientation w Higher Sampling (Lying on Charger Side) July 20th
# 14827 - Pool Displacement Control w Higher Sampling (Jul 23)
# 14888 - First Buoy Calibration Experiment (July 30)
# 15218 - Jasmine's Second Ride Sesh filmed with GoPro (Aug 29) //no footage
# 15629 - Jasmine's First Ride Sesh filmed with VIRB (Oct. 24) //first labelled footage!
# 15669 - Jasmine's Second Ride Sesh filmed with VIRB (Nov. 7) //second labelled footage!
# 15692 - Jasmine's 3rd Ride Sesh filmed with VIRB (Nov. 9) //third labelled footage!
# 15686 - Jasmine's 4th Ride Sesh filmed with VIRB (Nov. 11) //fourth labelled footage!


#%% Fin ID scraper
# Input fin ID, get all ride IDs
# base URL to which we'll append given fin IDs
fin_url_base = 'http://surf.smartfin.org/fin/'

# Look for the following text in the HTML contents in fcn below
str_id_ride = 'rideId = \'' # backslash allows us to look for single quote
str_id_date = 'var date = \'' # backslash allows us to look for single quote

#%% Ride ID scraper
# Input ride ID, get ocean and motion CSVs
# Base URL to which we'll append given ride IDs
ride_url_base = 'https://surf.smartfin.org/ride/'

# Look for the following text in the HTML contents in fcn below
str_id_csv = 'img id="temperatureChart" class="chart" src="' 



"""
Smartfin Web Scrape API is an interface that allows smartfin users to get data of their smartfin ride. This module interacts with both the smartfin website and CDIP THREDDS API to get smartfin and CDIP data. 
"""
class RideModule:
    
    def __init__(self): 
        print('ride initialized')
 

        
    # MAIN RIDE FUNCTION
    def get_ride_data(self, ride_id, buoys, convert_imu=True):
        """
        adds a ride dataframe to this dictionary 
        
        """
        # get df from ride number
        # get given ride's CSV from its ride ID using function above
        mdf, odf = self.get_csv_from_ride_id(ride_id) 

        latitude = mdf['Latitude'].mean() / 100000
        longitude = mdf['Longitude'].mean() / 100000
                       
        #Drop the latitude and longitude values since most of them are Nan:
        # mdf_dropped = mdf.drop(columns=['Latitude', 'Longitude'])
        mdf_dropped = mdf.drop(['Latitude', 'Longitude'], axis=1)

        #Drop the NAN values from the motion data:
        mdf = mdf_dropped.dropna(axis=0, how='any')
        
        if len(mdf) == 0 or len(odf) == 0:
            print('ERROR: Ride has no valid data, returning...')
            return {}
            
        # convert imu data 
        if(convert_imu):
            mdf = mdf.apply(lambda reading: reading / 512 * 9.80665 - 9.80665 
                                                         if reading.name == 'IMU A2'
                                                         else reading)
            mdf = mdf.apply(lambda reading: reading / 512 * 9.80665
                                                         if reading.name == 'IMU A1' or reading.name == 'IMU A3'
                                                         else reading)

            # convert time into seconds
            mdf['Time'] = [time / 1000 for time in mdf['Time']]

        

        odf_dropped = odf.drop(['salinity', 'Calibrated Salinity', 'Salinity Stable', 'pH', 'Calibrated pH', 'pH Stable'], axis=1)
        odf = odf_dropped.dropna(axis=0, how='any')
        print('df length before water data: ', len(mdf))
        mdf, odf = self.get_water_data(mdf, odf) 
        print('df length after water data: ', len(mdf))

        # get timeframe
        start_time, end_time = self.get_timeframe(mdf)
        print(f'calculated start_time: {start_time}')
        print(f'calculated end_time: {end_time}')
        
    
        # get nearest CDIP buoy
        mean_CDIP, means_CDIP, temp_CDIP, temps_CDIP, nearest_CDIP = self.CDIP_web_scrape(start_time, end_time, latitude, longitude, buoys)
        print(f'retrieved nearest CDIP buoy: {nearest_CDIP}')
        print(f'retrieved CDIP mean height for ride: {mean_CDIP}')
        print(f'retrieved CDIP mean temp for ride: {temp_CDIP}')

        height_smartfin, height_list, height_sample_rate = self.calculate_ride_height(mdf)
        temp_smartfin, temp_list, temp_sample_rate = self.calculate_ride_temp(odf)

        print('uploading ride data to database...')

        loc1, loc2, loc3 = self.get_nearest_city(latitude, longitude)

        # format data into dict for ride model
        data = {
            'rideId': ride_id, 
            'loc1': loc1,
            'loc2': loc2,
            'loc3': loc3,
            'startTime': start_time,
            'endTime': end_time,
            'heightSmartfin': height_smartfin,
            'heightList': height_list, 
            'heightSampleRate': height_sample_rate,
            'tempSmartfin': temp_smartfin,
            'tempList': temp_list,
            'tempSampleRate': temp_sample_rate,
            'buoyCDIP': nearest_CDIP, 
            'heightCDIP': mean_CDIP, 
            'tempCDIP': temp_CDIP, 
            'latitude': latitude,
            'longitude': longitude,
            'motionData': mdf.to_csv(),
            'oceanData': odf.to_csv(),
        }
    
        return data
        
            
        

    # HELPER FUNCTIONS
    def get_ride_height(self, ride_id, mdf):
        mdf_str = StringIO(mdf)
        mdf = pd.read_csv(mdf_str)

        print('updating heights')
        filt = double_integral_bandpass_filter()
        height_smartfin, height_list, height_sample_rate = filt.calculate_ride_height(mdf)
        print(f'updated height for ride {ride_id}: {height_smartfin} ')
        return height_smartfin


    
    # these two functions are temporary and will be edited when we refine them
    def calculate_ride_height(self, mdf): 
        
        filt = double_integral_bandpass_filter()
        height_smartfin, height_list, height_sample_rate = filt.calculate_ride_height(mdf)

        print(f'calculated smartfin significant wave height: {height_smartfin}')
        print(f'height reading sample rate: {height_sample_rate}')
        return height_smartfin, height_list, height_sample_rate 
        
        

    def calculate_ride_temp(self, odf):
        temps = odf['Calibrated Temperature 1']
        temp = temps.mean()
        temps = list(temps)
        print(f'calculated smartfin ride temp: {temp}')
        tempSampleRate = (int(odf.iloc[1]['Time']) - int(odf.iloc[0]['Time'])) / 1000
        print(f'temperature reading sample rate: {tempSampleRate}')

        return temp, temps, tempSampleRate


    def get_nearest_city(self, latitude, longitude):
        key = "AIzaSyCV3zZ2YhNOsf9DN8CvSiH1NBJC3XdMYs4"
        url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&sensor=true&key={key}'
        response = requests.get(url).json()
        loc1 = (response['results'][0]['address_components'][2]['long_name'])
        loc2 = (response['results'][0]['address_components'][3]['long_name'])
        loc3 = (response['results'][0]['address_components'][4]['long_name'])
        
        return loc1, loc2, loc3


    
    # filter motion and ocean dataframes to only hold readings taken from when the surfer is in the water
    def get_water_data(self, mdf, odf):

        temps = odf['Calibrated Temperature 1']
        threshold = temps.std() / 2
        med = temps.median()
#         print('med: ', med)
#         print('threshold: ', threshold)
#         print('temps: ', temps)

        mdf, odf = self.remove_before_entrance(mdf, odf, threshold, med)
#         print('after entreance: ', len(mdf))
        mdf, odf = self.remove_after_exit(mdf, odf, threshold, med)
#         print('aaaaaaaaaaaaaaa')
#         print('after exit', len(mdf))
        return mdf, odf
    
    
    # remove readings from ocean and motion dataframes where surfer is on land before entering the water
    def remove_before_entrance(self, mdf, odf, threshold, med):

        # get temperature series
        temps = odf['Calibrated Temperature 1']
        enter_index = self.get_water_entrance_index(temps, threshold, med)

        # get the time where the surfer enters the water in the ocean dataframe
        startTime = odf.iloc[enter_index]['Time']
        startTime /= 1000

        # find the index in motion dataframe that matches with start index calculated from ocean dataframe
        startIdx = mdf.iloc[(mdf['Time']-startTime).abs().argsort()[:1]]
        return mdf.loc[startIdx.index[0]:], odf.tail(len(odf) - enter_index)


    # calculate the index in ocean dataframe that the surfer enters the water
    def get_water_entrance_index(self, temps, threshold, med):

        above = False
        count = 0
        consecutiveWithin = 0

        # calculate the index at the point where the temperature readings fall within the threshold consecutively
        for time, reading in temps.items():
            if abs(reading - med) < threshold:
                if above == True:
                    above = False
                else:
                    consecutiveWithin += 1

                # if the temperatures fall within the threshold consecutively, then we can assume the surfer is in the water
                if consecutiveWithin > 10:
                    return count

                above = False

            else:
                above = True
                consecutiveWithin = 0
            count += 1 

        return firstInstance
    
    # remove readings from ocean and motion dataframes where surfer is on land after exiting the water
    def remove_after_exit(self, mdf, odf, threshold, med):
        
        # get the temperature series
        temps = odf['Calibrated Temperature 1']
#         print('temps: ', temps)
        # get the index where surfer exits the water
        exit_index = self.get_water_exit_index(temps, threshold, med)
#         print('exit index: ', exit_index)

        # get the time where the surfer enters the water in the ocean dataframe
        end_time = odf.iloc[exit_index]['Time']
        end_time /= 1000

        # find the index in motion dataframe that matches with end index calculated from ocean dataframe
        end_idx = mdf.iloc[(mdf['Time']-end_time).abs().argsort()[:1]]
        return mdf.loc[:end_idx.index[0]], odf.head(exit_index)


    # calculate the index in ocean dataframe that the surfer enters the water
    def get_water_exit_index(self, temps, threshold, med):
        above = False
        count = 0

        # calculate the index at the last point where the temperature readings transition from within to outside the threshold 
        for time, reading in temps.items():
            if abs(reading - med) > threshold:

                # record index where temperature transition from within to outside the threshold
                if above == False:
                    above = True
                    firstInstance = count

                above = True

            else:
                above = False
                firstInstance = -1
            count += 1 
            
       

        return firstInstance
    


    # Find nearest value in ncTime array to inputted UNIX Timestamp
    def find_nearest(self, array, value):
        idx = (np.abs(array-value)).argmin()
        return array[idx]
    
    
    # Convert human-formatted date to UNIX timestamp
    def getUnixTimestamp(self, humanTime, dateFormat):
        unixTimestamp = int(time.mktime(datetime.datetime.strptime(humanTime, dateFormat).timetuple()))
        return unixTimestamp
    
    
    
    
    def get_csv_from_ride_id (self, ride_id):
        # Build URL for each individual ride
        ride_url = ride_url_base+str(ride_id)
        print(f'fetching ride from: {ride_url}')

        # Get contents of ride_url
        html_contents = requests.get(ride_url).text

        # Find CSV identifier 
        loc_csv_id = html_contents.find(str_id_csv)

        # Different based on whether user logged in with FB or Google
        offset_googleOAuth = [46, 114]
        offset_facebkOAuth = [46, 112]
        if html_contents[loc_csv_id+59] == 'f': # Facebook login
            off0 = offset_facebkOAuth[0]
            off1 = offset_facebkOAuth[1]
        else: # Google login
            off0 = offset_googleOAuth[0]
            off1 = offset_googleOAuth[1]

        csv_id_longstr = html_contents[loc_csv_id+off0:loc_csv_id+off1]
        
        # Stitch together full URL for CSV
        # other junk URLs can exist and break everything
        if ("media" in csv_id_longstr) & ("Calibration" not in html_contents): 

            sample_interval = '1000ms'

            mdf_url = f'https://surf.smartfin.org/{csv_id_longstr}Motion.CSV'
            print(f'fetching motion data from: {mdf_url}')
            mdf = pd.read_csv(mdf_url, parse_dates = [0])
            mdf = mdf.set_index('UTC', drop = True, append = False)
            mdf = mdf.resample(sample_interval).mean()
            odf_url = f'https://surf.smartfin.org/{csv_id_longstr}Ocean.CSV'
            print(f'fetching ocean data from: {odf_url}')
            odf = pd.read_csv(odf_url, parse_dates = [0])
            odf = odf.set_index('UTC', drop = True, append = False)
            odf = odf.resample(sample_interval).mean()

            return mdf, odf

        else:
            print('here')
            df = pd.DataFrame() # empty DF just so something is returned
            return df
      
    

    
    def get_timeframe(self, df):
        
        # get the times of the first and last reading
        df = df.reset_index()
        df = df.set_index('UTC')
        print('df length: ', len(df))

        start_time = df.index[0].timestamp()
        end_time = df.index[-1].timestamp()
        print('TYPEYTPYPESDF: ', type(df.index[0]))
        return start_time, end_time
    

        
        
    def CDIP_web_scrape(self, start_time, end_time, latitude, longitude, buoys):
                
        # get nearest station
        station = self.get_nearest_station(latitude, longitude, buoys)
        
        data_url = f'http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/{station}p1/{station}p1_historic.nc'
        print(f'retriving CDIP wave heights from: {data_url}')
        
        # netCDF data object fetched from CDIP API
        nc = netCDF4.Dataset(data_url)
        
        # GET WAVE DATA
        # UNIX based time from 1991-yeardate in 30 minute increments
        waveTime = nc.variables['waveTime'][:]

        # wave heights
        Hs = nc.variables['waveHs'][:]
        
        # find the 30 minute chunks that correspond with smartfin ride timeframe
        unixstart = start_time
        nearest_date = self.find_nearest(waveTime, unixstart)  # Find the closest unix timestamp
        wave_start_index = np.where(waveTime==nearest_date)[0][0]  # Grab the index number of found date

        unixend = end_time
        future_date = self.find_nearest(waveTime, unixend)  # Find the closest unix timestamp
        wave_end_index = np.where(waveTime==future_date)[0][0]  # Grab the index number of found date 

        if (wave_start_index - wave_end_index == 0): wave_end_index += 1

        
        # account for index offsets
#         wave_start_index -= 14
#         wave_end_index -= 14
        
        print(f'calculating significant wave height between {start_time} - {end_time}')
        
        # all wave height averages per 30 minute increments over each month
        ride_hs = Hs[wave_start_index:wave_end_index]
        ride_hs = ride_hs.data
       
    
    
        # GET TEMPERATURE DATA
        # UNIX based time from 1991-yeardate in 30 minute increments
        sstTime = nc.variables['sstTime'][:]
        # ocean temp
        Ts = nc.variables['sstSeaSurfaceTemperature'][:]
        
        # find the 30 minute chunks that correspond with smartfin ride timeframe
        unixstart = start_time
        nearest_date = self.find_nearest(sstTime, unixstart)  # Find the closest unix timestamp
        temp_start_index = np.where(sstTime==nearest_date)[0][0]  # Grab the index number of found date

        unixend = end_time
        future_date = self.find_nearest(sstTime, unixend)  # Find the closest unix timestamp
        temp_end_index = np.where(sstTime==future_date)[0][0]  # Grab the index number of found date 
        
#         temp_start_index -= 14
#         temp_end_index -= 14
                
        print(f'calculating significant wave height between {start_time} - {end_time}')
            
        # get ocean surface temperature during ride
        ride_ts = Ts[temp_start_index:temp_end_index]
        ride_ts = ride_ts.data
   
        # CALCULATE MEANS of each month dataset in box_data
        mean_h = ride_hs.mean()
        mean_t = ride_ts.mean()
        
        print(f'mean wave height: {mean_h}')
        print(f'mean ocean temp: {mean_t}')
        
        return mean_h, list(ride_hs), mean_t, list(ride_ts), station


    def get_CDIP_stations(self):
        
        # get all active buoys with archived data
        stns = self.get_active_buoys()
        buoys = []
        count = 0

         # iterate through 0-450 (station numbers are from 28-433 with gaps in between)
        for i in stns:
            
            count += 1

            # format i into a 3 digit string
            i = str(i)
            if len(i) == 1:
                i = '00' + i
            elif len(i) == 2:
                i = '0' + i

            # see if there is a station with the current iteration number
            try:
                data_url = 'http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/' + i + 'p1/' + i+ 'p1_historic.nc'
                nc = netCDF4.Dataset(data_url)

                # get latitude and longitude of current station
                nc_latitude = nc.variables['metaStationLatitude'][:]
                nc_longitude = nc.variables['metaStationLongitude'][:]
                nc_latitude = float(nc_latitude.data)
                nc_longitude = float(nc_longitude.data)

                buoys.append({'buoyNum': i, 'latitude': nc_latitude, 'longitude': nc_longitude})

            except OSError as err:
                continue

        return buoys
   
    
    def get_nearest_station(self, latitude, longitude, buoys):
        # intialize the lowest distance to be some rediculously big number
        lowest_distance = 1000000000
        stn = -1
        count = 0

        for buoy in buoys:

            b_latitude = buoy['latitude']
            b_longitude = buoy['longitude']

            curr_distance = abs(b_latitude - latitude) + abs(b_longitude - longitude)
            if curr_distance < lowest_distance:
                lowest_distance = curr_distance
                stn = buoy['buoyNum']
            count += 1


        if stn == -1:
            print('no station found error')
            
        return stn
                


    def get_active_buoys(self):
        # CDIP active buoys URL
        url="http://cdip.ucsd.edu/m/deployment/station_view/?mode=active"

        # Make a GET request to fetch the raw HTML content
        html_content = requests.get(url).text

        # Parse the html content
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find("table")
        table_data = table.tbody.find_all("tr")  # contains 2 rows
        stns = []
        for node in table_data:
            try:
                stn = node.findAll('td', text=True)[0]
                stns.append(stn.text.strip(' '))
            except:
                continue

        return stns
        


    
    # def get_nearest_station(self, latitude, longitude):

    #     # get all active buoys with archived data
    #     stns = self.get_active_buoys()
   
    #     # intialize the lowest distance to be some rediculously big number
    #     lowest_distance = 1000000000
    #     stn = -1
    #     count = 0

    #     # url = 'http://127.0.0.1:8000/ride/buoylist/'
    #     # print(requests.get(url))

    #     # iterate through 0-450 (station numbers are from 28-433 with gaps in between)
    #     for i in stns:
            
    #         count += 1

    #         # format i into a 3 digit string
    #         i = str(i)
    #         if len(i) == 1:
    #             i = '00' + i
    #         elif len(i) == 2:
    #             i = '0' + i

    #         # see if there is a station with the current iteration number
    #         try:
    #             data_url = 'http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/' + i + 'p1/' + i+ 'p1_historic.nc'
    #             nc = netCDF4.Dataset(data_url)
 
    #             # get latitude and longitude of current station
    #             nc_latitude = nc.variables['metaStationLatitude'][:]
    #             nc_longitude = nc.variables['metaStationLongitude'][:]
                
    #             print('', end='\r')
    #             print(f'checking for nearest buoy... {count}/{len(stns)}')

    #             # if the current station distance is lower than the lowest distance so far, save it
    #             curr_distance = abs(nc_latitude - latitude) + abs(nc_longitude - longitude)
    #             if curr_distance < lowest_distance:
    #                 lowest_distance = curr_distance
    #                 stn = i
    #             else: continue

    #         except OSError as err:
    #             continue

    #     if stn == -1:
    #         print('no station found error')
            
    #     return stn
    


       
  # def get_nearest_city(self, latitude, longitude):
    #     key = "AIzaSyCV3zZ2YhNOsf9DN8CvSiH1NBJC3XdMYs4"
    #     url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&sensor=true&key={key}'
    #     fetch(url)
    #         .then(response => response.json())
    #         .then(data => {
    #             try {
    #                 console.log(data['results'][0]['address_components'])
    #                 setRideLocation({
    #                     city: data['results'][0]['address_components'][2]['long_name'], 
    #                     state: data['results'][0]['address_components'][4]['short_name']
    #                 })
    #             } catch {
    #                 console.log('no')
    #             }
                    
    #         })

    # def post_motion_data(self, df, model, ride_id):

    #     print('uploading motion data to db...')

    #     r = model

    #     for row in df.iterrows():
    #         data = row[1].to_dict()
    #         r = model(
    #             time=data['Time'],
    #             imuA1=data['IMU A1'],
    #             imuA2=data['IMU A1'],
    #             imuA3=data['IMU A1'],
    #             imuG1=data['IMU A1'],
    #             imuG2=data['IMU A1'],
    #             imuG3=data['IMU A1'],
    #             imuM1=data['IMU A1'],
    #             imuM2=data['IMU A1'],
    #             imuM3=data['IMU A1'],
    #             rideId=ride_id,
    #         )
    #         r.save()




    # def post_ocean_data(self, df, model, ride_id):

    #     print('uploading ocean data to db...')

    #     for row in df.iterrows():
    #         data = row[1].to_dict()
    #         r = model(
    #             time=data['Time'],
    #             temp1=data['Temperature 1'],
    #             calibratedTemp1=data['Calibrated Temperature 1'],
    #             temp1Stable=data['Temperature 1 Stable'],
    #             temp2=data['Temperature 2'],
    #             calibratedTemp2=data['Calibrated Temperature 2'],
    #             temp2Stable=data['Temperature 2 Stable'],
    #             rideId=ride_id,
    #         )
    #         r.save()
    #
    # 
    #         print('finished uploading.')

