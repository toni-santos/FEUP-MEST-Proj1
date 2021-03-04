import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn import datasets, linear_model, cluster
from sklearn.model_selection import train_test_split

import parser
import utilities


###Function Definitions###


#TODO: Graphics 
def draw_graphic():
    """
    Types of graphics needed:
    #Line chart
    #Bar chart
    #Candlestick chart
    """

    pass












if __name__ == '__main__':

    #Excel sheets
    sheet_names = ['project1.xlsx', 'classificationdata.xlsx', 'wscdata.xlsx']
    public_dataset = 'dev.csv'

    #File path

    FILE_PATH = f'/home/gui1612/Documents/files/{public_dataset}'


    #Parsing the excel sheet with pandas
    if FILE_PATH[-3:] == 'sxl':
        data = pd.read_excel(FILE_PATH)
    else:    
        data = pd.read_csv(FILE_PATH)


    # kmeans = cluster.KMeans(n_clusters=2,random_state=0).fit(data)

    data = pd.DataFrame(data)
    data.values.tolist()


    #Testing

    print(data)    

