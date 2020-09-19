
from scipy import stats
from scipy import constants
from scipy import signal #added
from scipy.interpolate import CubicSpline
from scipy.interpolate import interp1d
from scipy.integrate import simps
from scipy.integrate import cumtrapz
from scipy import integrate

import random

import numpy as np



class double_integral_bandpass_filter:
    
    
    # these two functions are temporary and will be edited when we refine them
    def calculate_ride_height(self, mdf): 
        mdf = self.process_IMU(mdf)
        print("chunking data")
        accs, times, chunk_len = self.chunk_data(mdf['IMU A2'], mdf['Time'])

        print("getting displacements")
        integral, displacements = self.get_displacement_data(accs, times)
        
        integral *= 2.65
        print(f'calculated smartfin significant wave height: {integral}')
        print(f'height reading sample rate: {chunk_len}')
        return integral, displacements, chunk_len
    
    
    
    def process_IMU(self, df):
        df = df.head(2160)
        df = df[360:2160]
        print(df['IMU A2'].max())
        mean = df['IMU A2'].mean()
        std = df['IMU A2'].std()
        Upperbound = mean+(2.1*std)
        Lowerbound = mean-(2.1*std)
        Up = (mean+.5)
        Low = (mean-.5)
        print('mean is: ' + str(mean))
        print('std. dev. is: ' + str(std))
        print('Upperbound is: ' + str(Upperbound))
        print('Lowerbound is: ' + str(Lowerbound))
        df.loc[df['IMU A2'] > Upperbound, 'IMU A2'] = float(random.uniform(Up, Low))
        df.loc[df['IMU A2'] < Lowerbound, 'IMU A2'] = float(random.uniform(Up, Low))
        print(df['IMU A2'].max())
        return df
        
        
        
    def chunk_data(self, acc_array, time_array):
        chunk_len = 10
        times = []
        accs = []
            
        for i in range(int(len(acc_array) / chunk_len)):
            accs.append(acc_array[i*chunk_len:(i + 1)*chunk_len])
            times.append(time_array[i*chunk_len:(i + 1)*chunk_len])
        
        return accs, times, chunk_len
    

   
    def double_integral_bandpass(self, dacc_array, time_array, lowcut, highcut, fs, order):
        butter_lfilter = self.butter_bandpass_lfilter(dacc_array, lowcut, highcut, fs)


        #First integral is the velocity:
        v_integral = integrate.cumtrapz(x=time_array, y=butter_lfilter, initial=0)
        detrend_v_integral = signal.detrend(v_integral)

        v_butter_filter_integral = self.butter_bandpass_lfilter(detrend_v_integral, lowcut, highcut, fs, order=5)
        detrend_v_integral = signal.detrend(v_butter_filter_integral)


        #Second integral is the displacment:
        disp_integral = integrate.cumtrapz(x=time_array, y=v_butter_filter_integral, initial=0)
        detrend_disp_integral = signal.detrend(disp_integral)

        disp_butter_filter_integral = self.butter_bandpass_lfilter(detrend_disp_integral, lowcut, highcut, fs, order=5)
        detrend_disp_butter_integral = signal.detrend(disp_butter_filter_integral)
        return detrend_disp_butter_integral
            

    def get_displacement_data(self, accs, times):

        fs = 5 #redefine the sampling frequency

        order=6
        lowcut = 0.09
        highcut = 1.0
        
        integrals = []
        for i in range(len(accs)):
            dacc_array = signal.detrend(accs[i])    
            integrals.append(self.double_integral_bandpass(dacc_array, times[i], lowcut, highcut, fs, order))
            
        displacements = []
        for integral in integrals:
            displacements.append(integral.max() - integral.min())

        displacementsSorted = np.sort(displacements)
        displacementsSorted = np.flip(displacementsSorted)
        third = int(len(displacementsSorted) * .33)
        displacement = displacementsSorted[0:third].mean()

        return displacement, displacements

    


    ## Butter Filters for Bandpass:
    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = signal.butter(order, [low, high], btype='band')
        return b, a

    def butter_bandpass_lfilter(self, data, lowcut, highcut, fs, order=5):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = signal.lfilter(b, a, data)
        return y

    def butter_bandpass_filtfilt(self, data, lowcut, highcut, fs, order=5):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = signal.filtfilt(b, a, data)
        return y



    ##Butter Filters for Highpass:
    def butter_highpass(self, highcut, fs, order=5):
        nyq = 0.5 * fs
        high = highcut / nyq
        b, a = signal.butter(order, high, btype='high')
        return b, a

    def butter_highpass_lfilter(self, data, highcut, fs, order=5):
        b, a = butter_lowpass(highcut, fs, order=order)
        y = signal.lfilter(b, a, data)
        return y



    ##Butter Filters for Lowpass:
    def butter_lowpass(self, lowcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        b, a = signal.butter(order, low, btype='low')
        return b, a

    def butter_lowpass_lfilter(self, data, lowcut, fs, order=5):
        b, a = butter_lowpass(lowcut, fs, order=order)
        y = signal.lfilter(b, a, data)
        return y