import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from Geometry3DWrapper import *

folder = "./NL45" # "./PL45"
inpol = "0_-1_0" # 0_1_0
thetas = [i*3 for i in range(16)]
#thetas = [21]
polas = [i*2 for i in range(81)]

fs = ['polarizationData_0_0_1.csv', 'polarizationData_0_0_-1.csv', 'polarizationData_0_1_0.csv', 'polarizationData_0_-1_0.csv']

class dataFormatter:
    def __init__(self):
        self.xaxis = wVector(1,0,0)
        self.yaxis = wVector(0,1,0)
        self.zaxis = wVector(0,0,1)

        self.xaxis1 = wVector(1,0,0)
        self.yaxis1 = wVector(0,1,0)
        self.zaxis1 = wVector(0,0,1)

    def convertOriginalCSV(self, folder, theta, pola, pol):
        '''
        Input:
        @theta: theta 
        @pola: porimeter angle
        @pol: input polarization, expressed in "s1_s2_s3"
        Output:
        a dataframe with input angle and output angle calculated: 11 columns: ['InTheta', 'InPhi','InPol', 'OutTheta', 'OutPhi', 'Power', 'S1', 'S2', 'S3', 'Azimuthal','Ellipticity']
        '''
        fp = os.path.join(folder, "theta{}_pola{}.csv".format(theta, pola))
        print("processing the file: {}...".format(fp))
        df  = pd.read_csv(fp)
        df.drop_duplicates(inplace=True)
        df.replace("", float("NaN"), inplace=True)
        df.dropna(axis=0, how='any', inplace=True)
    
        startTime = int(df.iloc[0].startTime)
        endTime = int(df.iloc[0].endTime)
    
        thetaRotation = self.yaxis.rotateMatrix(theta)
        self.zaxis1 = self.zaxis.rotateByMatrix(thetaRotation)
        detector = wVector(0,-1,0).rotateByAxis(self.zaxis, 20 + pola) # detector vector

        df_map = pd.DataFrame({ 'InTheta':pd.Series(dtype='float'), 'InPhi':pd.Series(dtype='float'), 'OutTheta':pd.Series(dtype='float'), 'OutPhi':pd.Series(dtype='float'), 'Power':pd.Series(dtype='float'), 'S1':pd.Series(dtype='float'), 'S2':pd.Series(dtype='float'), 'S3':pd.Series(dtype='float'), 'Azimuthal':pd.Series(dtype='float'), 'Ellipticity':pd.Series(dtype='float') })
        for index,row in df.iterrows():
            ts = int(row.loc['Polarimeter Time'])
            if ts < startTime or ts > endTime: continue

            phi = (ts - startTime) * 90 / (endTime - startTime)
            phi = 90 - phi
            phiRotation = self.zaxis1.rotateMatrix(-phi)
            rotation = phiRotation.dot(thetaRotation)
            self.xaxis1 = self.xaxis.rotateByMatrix(rotation)
            self.yaxis1 = self.yaxis.rotateByMatrix(rotation)
            lightray = wVector(-1,0,0)
            nvec = lightray.rotateByMatrix(rotation) # normal vector to the sample
            if nvec * detector > 0: continue # we record the reflected light

            if(nvec.parallel(lightray)):
                inTheta = 0
                inPhi = 0
            else:
                inTheta = math.degrees( nvec.angle( lightray )) # input theta
                projected = lightray.projectOnPlane(nvec)
                inPhi = math.degrees( projected.angle(self.yaxis1) ) # input phi

            if( nvec.parallel(detector) ):
                outTheta = 0
                outPhi = 0
            else:
                nvec = nvec * -1 # normal vector to the sample
                outTheta = math.degrees( nvec.angle(detector) ) # output theta
                projected_det = detector.projectOnPlane(nvec)
                outPhi = math.degrees( projected_det.angle(self.yaxis1) ) # output phi

#            inphi = 90 - phi
#            #outphi = 160 - pola - phi
#            outphi = pola + 20 - phi
#            if outphi > 90 or outphi < -90: continue

            s1 = np.cos(2*row.azimuthal) * np.cos(2*row.ellipticity)
            s2 = np.sin(2*row.azimuthal) * np.cos(2*row.ellipticity)
            s3 = np.sin(2*row.ellipticity)
            df_map = df_map.append( {'InTheta': round(inTheta, 3), 'InPhi': round(inPhi, 3), 'OutTheta': round(outTheta,3), 'OutPhi': round(outPhi,3), 'Power': row.Power, 'S1':round(s1, 3), 'S2':round(s2, 3), 'S3':round(s3,3), 'Azimuthal':round(row.azimuthal, 3), 'Ellipticity':round(row.ellipticity,3)}, ignore_index = True )
        df_map.insert(0, 'InPol', [pol]*len(df_map))
        df_map.sort_values( by=['InPol', 'InTheta', 'InPhi'], inplace=True )
    
        return df_map
    
    def combineOriginalCSVs(self, folder, InPol, outf):
        '''
        Input:
        @folder: the folder path to where your CSVs files are located
        @InPol: the input polarization, expressed as s1_s2_s3
        @outf: the output CSV file name
        Output:
        a combined dataframe with input angle and output angle calculated: 11 columns: ['InTheta', 'InPhi','InPol', 'OutTheta', 'OutPhi', 'Power', 'S1', 'S2', 'S3', 'Azimuthal','Ellipticity']
        and write to the output CSV file
        '''
        df = pd.DataFrame()
        for theta in thetas:
            for pola in polas:
                _df = self.convertOriginalCSV(folder, theta, pola, InPol)
                df = pd.concat([df, _df], ignore_index=True)
        df.sort_values(['InPol', 'InTheta', 'InPhi', 'OutTheta', 'OutPhi'],inplace=True)
        df.to_csv(outf)
        return df
    
    def mergeCSVs(self, fs, outf):
        '''
        :param @fs: a list of file names to be merged
        @outf: output file name
        '''
        df = pd.DataFrame()
        for f in fs:
            d = pd.read_csv(f)
            df = pd.concat([df, d], ignore_index=True)
        df.sort_values( ['InPol', 'InTheta', 'InPhi', 'OutTheta', 'OutPhi'],inplace=True )
        df.to_csv(outf)
        return df


if __name__ == "__main__":
    myformatter = dataFormatter()
#    myformatter.combineOriginalCSVs(folder, inpol, "polarizationData_{}.csv".format(inpol))

    myformatter.mergeCSVs(fs, 'polarizationData_all.csv')
