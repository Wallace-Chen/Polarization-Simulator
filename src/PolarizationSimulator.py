import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
import sys
from Geometry3D import *

np.set_printoptions(threshold=np.inf)
pd.set_option("display.max_rows", None, "display.max_columns", None)


class SampleSimulator:
    def __init__(self, fdata):
        '''
        Constructor
        '''
        self.df = pd.read_csv(fdata)
        self.precision = 0.375 # angle precision
#        self.precisionPhi = 0.375 # angle precision threshold (for input phi angle), not due to measurement, to ease the simulation
#        self.precisionTheta = 3 # theta angle precision

    # or using scipy package from: https://stackoverflow.com/questions/7778343/pcolormesh-with-missing-values
    def interpolate(self, d, ind):
        d = list(d)
        left = 0
        right = 0
        i = 1
        while ind-i >=0 and np.abs(d[ind-i]) > 0:
            left = d[ind-i]
            break
        i = 1
        while ind+i<len(d) and np.abs( d[ind+i] ) > 0:
            right = d[ind+i]
            break
        if left == 0 or right == 0: print("Warning: cannot interpolate data!")
        return (left+right) / 2

    def fillData(self, data, intheta, inphi):
        x_low = 0
        x_high = 360
        y_low = 0
        y_high = 90
        x = np.arange(x_low, x_high, self.precision)
        y = np.arange(y_low, y_high, self.precision)
        [X, Y] = np.meshgrid(x, y)
        shape = X.shape
        power = np.zeros(shape)
        s1 = np.zeros(shape)
        s2 = np.zeros(shape)
        s3 = np.zeros(shape)
        for index,row in data.iterrows():
            diff = row.InPhi - inphi
            theta = row.OutTheta
            phi = row.OutPhi + diff # due to the symmetry along the phi direction, only valid for circularly polarized light!
            phi = ( phi + 360 ) % 360
            nrow = int((theta - y_low) / self.precision)
            ncol = int((phi - x_low) / self.precision)
            power[nrow][ncol] = row.Power
            s1[nrow][ncol] = row.S1
            s2[nrow][ncol] = row.S2
            s3[nrow][ncol] = row.S3
#        tmp = np.where(np.abs(power) > 0)
#        valid_rows = list(set(list(tmp[0])))
#        for nrow in valid_rows:
#            empty_columns = list(np.where( power[nrow,:] == 0 )[0])
#            valid_columns = list(set(range(0, shape[1])) - set(empty_columns))

#            empty_columns = [x for x in empty_columns if (x > valid_columns[0]) and (x < valid_columns[-1]) ]
#            for ncol in empty_columns:
#                power[nrow][ncol] = self.interpolate(list(power[nrow,:]), ncol)
#                s1[nrow][ncol] = self.interpolate(list(s1[nrow,:]), ncol)
#                s2[nrow][ncol] = self.interpolate(list(s2[nrow,:]), ncol)
#                s3[nrow][ncol] = self.interpolate(list(s3[nrow,:]), ncol)

        power = power / np.amax(power)
        s1[power<=0] = np.nan # illegal data if power is zero or below
        s2[power<=0] = np.nan
        s3[power<=0] = np.nan
        power[power<=0] = np.nan
        return [X, Y, power, s1, s2, s3]

#    def fillData(self, data):
#        x_low = -90
#        x_high = 90
#        y_low = -45
#        y_high = 45
#        _precisionPhi = 2
#        x = np.arange(x_low, x_high, _precisionPhi)
#        y = np.arange(y_low, y_high, self.precision)
#        [X, Y] = np.meshgrid(x, y)
#        shape = X.shape
#        power = np.zeros(shape)
#        s1 = np.zeros(shape)
#        s2 = np.zeros(shape)
#        s3 = np.zeros(shape)
#        for index,row in data.iterrows():
#            theta = row.OutTheta
#            phi = row.OutPhi
#            nrow = int((y_high - theta) / self.precision)
#            ncol = int((phi - x_low) / _precisionPhi)
#            power[nrow][ncol] = row.Power
#            s1[nrow][ncol] = row.S1
#            s2[nrow][ncol] = row.S2
#            s3[nrow][ncol] = row.S3
#        tmp = np.where(np.abs(power) > 0)
#        valid_rows = list(set(list(tmp[0])))
#        for nrow in valid_rows:
#            empty_columns = list(np.where( power[nrow,:] == 0 )[0])
#            valid_columns = list(set(range(0, shape[1])) - set(empty_columns))
#
#            empty_columns = [x for x in empty_columns if (x > valid_columns[0]) and (x < valid_columns[-1]) ]
#            for ncol in empty_columns:
#                power[nrow][ncol] = self.interpolate(list(power[nrow,:]), ncol)
#                s1[nrow][ncol] = self.interpolate(list(s1[nrow,:]), ncol)
#                s2[nrow][ncol] = self.interpolate(list(s2[nrow,:]), ncol)
#                s3[nrow][ncol] = self.interpolate(list(s3[nrow,:]), ncol)
#
#        power = power / np.amax(power)
#        s1[power<=0] = np.nan # illegal data if power is zero or below
#        s2[power<=0] = np.nan
#        s3[power<=0] = np.nan
#        power[power<=0] = np.nan
#        return [X, Y, power, s1, s2, s3]


    def draw(self, data, intheta, inphi):
        fig = plt.figure()

        [X, Y, power, s1, s2, s3] = self.fillData(data, intheta, inphi)

        fig, ax = plt.subplots(2, 2)
        f1 = ax[0,0].pcolor(X, Y, power, norm = LogNorm()) #, shading='auto')
        f2 = ax[0,1].pcolor(X, Y, s1, vmin = -1, vmax = 1) #, shading='auto')
        f3 = ax[1,0].pcolor(X, Y, s2, vmin = -1, vmax = 1) #, shading='auto')
        f4 = ax[1,1].pcolor(X, Y, s3, vmin = -1, vmax = 1) #, shading='auto')


        fig.colorbar(f1, ax=ax[0,0])
        fig.colorbar(f2, ax=ax[0,1])
        fig.colorbar(f3, ax=ax[1,0])
        fig.colorbar(f4, ax=ax[1,1])
        ax[0,0].set_title('Power')
        ax[0,1].set_title('S1')
        ax[1,0].set_title('S2')
        ax[1,1].set_title('S3')
        ax[0,0].set_xlabel('phi')
        ax[0,1].set_xlabel('phi')
        ax[1,0].set_xlabel('phi')
        ax[1,1].set_xlabel('phi')
        ax[0,0].set_ylabel('theta')
        ax[0,1].set_ylabel('theta')
        ax[1,0].set_ylabel('theta')
        ax[1,1].set_ylabel('theta')
        plt.show()
        

    def simulate(self, inpol, intheta, inphi):
        """
        simulte the stokes parameters on the detector plane given input light with (intheta, inphi) angle, with the polarization inpol
        @param:
            inpol: input polarization, expressed by S1_S2_S3
            intheta, inphi: angle of the input light. range of intheta: [0, 90], range of inphi: [0, 360].
                            For circular polarized input light, the system is assumed to be symmetric about the inphi angle, which means if 
                                we rotate the sample + the detector plane as a whole along phi direction, we get the same pattern on the detector.

                            For linearly polarized input light, the angle between the incident plane and the intput polarization would change
                                for different inphi angle, the inphi symmetry is not preserved.
        """
        df = self.df
        inphi = inphi
        intheta = intheta
        thetaPrecision = 1
        mulPhi = int(inphi / self.precision)
        mulTheta = int(intheta / thetaPrecision)
        d = []
        if inpol == "0_0_1" or inpol == "0_0_-1": # currently only consider circularly polarized light so that we can use the symmetry
            d = df.loc[ (df['InPol']==inpol) & (df['InTheta']>=mulTheta*thetaPrecision) & (df['InTheta']<(mulTheta+1)*thetaPrecision) ] 
#            d = df.loc[ (df['InPol']==inpol) & (df['InTheta']>=mulTheta*self.precision) & (df['InTheta']<(mulTheta+1)*self.precision) & (df['InPhi']>=(mulPhi*self.precision)) & (df['InPhi']<((mulPhi+1)*self.precision)) ]
#        d = d.iloc[0:80]
#        print(d)

        if len(d) == 0:
            print("Error, cannot find mapping data!")
            print("Only circularly polarized supported. Make sure theta within [0, 90], and phi within [90, 180]")
            return
        self.draw(d, intheta, inphi)


if __name__ == "__main__":
    mysim = SampleSimulator('./polarizationData_all.csv')
    mysim.simulate('0_0_1', 10, 30)
