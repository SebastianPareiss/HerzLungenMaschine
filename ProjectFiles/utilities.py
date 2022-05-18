# Import external packages

from multiprocessing.connection import wait
import pandas as pd
from datetime import datetime
import numpy as np
import re

# Classes 

class Subject():
    def __init__(self, file_name):

        ### Aufgabe 1: Interpolation ###

        __f = open(file_name)
        self.subject_data = pd.read_csv(__f)
        #Interpolation der Daten, mithilfe von 'quadratic' werden Lücken aus _f ausgeglichen
        #https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html
        self.subject_data = self.subject_data.interpolate(method='quadratic', axis=0) 
        #__splited_id = re.findall(r'\d+',file_name)
        #print(__splited_id)   
        self.subject_id = file_name.split(".csv")[0][-1] #Ausgleichen des Fehlers vom Dateipfad...Dateipfad hat immer nur Subject 2 hergegeben 
        self.names = self.subject_data.columns.values.tolist()
        self.time = self.subject_data["Time (s)"]        
        self.spO2 = self.subject_data["SpO2 (%)"]
        self.temp = self.subject_data["Temp (C)"]
        self.blood_flow = self.subject_data["Blood Flow (ml/s)"]
        print('Subject ' + self.subject_id + ' initialized')



        

### Aufgabe 2: Datenverarbeitung ###

#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.expanding.html

def calculate_CMA(df,n):  #Cumulative Moving average => mean of all previous values up to current value 
    return df.expanding(n).mean() #Befehl für CMA => DataFrame providing expanding window calculation
    
#https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html

def calculate_SMA(df,n):  #Simple Moving average => unweighted mean of previous K data
    return df.rolling(n).mean() #Befehl für SMA => DataFrame providing rolling window calculation