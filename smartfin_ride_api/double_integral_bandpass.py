
from scipy import stats
from scipy import constants
from scipy import signal #added
from scipy.interpolate import CubicSpline
from scipy.interpolate import interp1d
from scipy.integrate import simps
from scipy.integrate import cumtrapz
from scipy import integrate

import numpy as np



class double_integral_bandpass_filter:

   
    def double_integral_bandpass(self, dacc_array, time_array, lowcut, highcut, fs, order):
        butter_lfilter = self.butter_bandpass_lfilter(dacc_array, lowcut, highcut, fs, order=5)
        
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
        b, a = self.butter_lowpass(highcut, fs, order=order)
        y = signal.lfilter(b, a, data)
        return y



    ##Butter Filters for Lowpass:
    def butter_lowpass(self, lowcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        b, a = signal.butter(order, low, btype='low')
        return b, a

    def butter_lowpass_lfilter(self, data, lowcut, fs, order=5):
        b, a = self.butter_lowpass(lowcut, fs, order=order)
        y = signal.lfilter(b, a, data)
        return y