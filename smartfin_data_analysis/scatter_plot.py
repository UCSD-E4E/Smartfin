import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class smartfin_plot:

    def __init__(self):
        print('intialized')

    
    def scatter_plot(self, sig_heights, CDIP_means, scalar):
       
        fin = np.array(sig_heights)
        buoy = np.array(CDIP_means)
        fin3 = scalar*fin

        data_to_plot = pd.DataFrame({'Smartfin': fin, 'Buoy': buoy, 'fin_converted': fin3, 'diff1': abs(buoy-fin), 'diff2': abs(buoy-fin3)})


        x = list(range(0, len(data_to_plot)))

        #Original data plot
        plt.scatter(x, data_to_plot['Smartfin'], color='red')
        plt.scatter(x, data_to_plot['Buoy'], color='blue')
#         plt.legend(['Smartfin', 'Buoy'], loc=9)
        plt.xlabel('Session')
        plt.ylabel('Significant Wave Height [m]')
        plt.title('2017 Smartfin Height vs. CDIP Buoy Height', size=15)
        plt.grid()
        plt.show()

        error = (abs(data_to_plot['Buoy'] - data_to_plot['Smartfin']) / data_to_plot['Buoy']) * 100
        error = np.mean(error)
 
#         error = abs((1 - (data_to_plot['Buoy']/data_to_plot['Smartfin'])) *100)
#         error = np.mean(error)
        avgdiff1 = data_to_plot['diff1'].mean()
        print('mean error is ' + str(error) + '%')
#         print('average difference is ' + str(avgdiff1) + ' meters')
#         print('average difference is ' + str(avgdiff1*39.3701) + ' inches')
#         print('length is ' + str(len(data_to_plot)))

        #Converted data plot
        plt.scatter(x, data_to_plot['fin_converted'], color='red')
        plt.scatter(x, data_to_plot['Buoy'], color='blue')
#         plt.legend(['Smartfin', 'Buoy'], loc=9)
        plt.xlabel('Session')
        plt.ylabel('Significant Wave Height [m]')
        plt.title('2017 Smartfin Height vs. CDIP Buoy Height', size=15)
        plt.grid()
        plt.show()

        error3 = abs((1 - (data_to_plot['Buoy']/data_to_plot['fin_converted'])) *100)
        error3 = np.mean(error3)
        avgdiff2 = data_to_plot['diff2'].mean()
        print('mean error is ' + str(error3) + '%')
#        

    def plot_ride_accs(self, times, accs):
        
        plt.plot(times, accs)
        splt.show()