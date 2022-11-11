# Copyright (c) Sarus Systems Systems Limited 2022  

import numpy as np
import pandas as pd

class MonitorUtils:    
     
    def __init__(self, API_DSName1):
        self.API_DSName1 = API_DSName1

    def get_display_data(self, dictionary):
        rows = dictionary['Rows']
        corrections = dictionary['Corrections']
        df = pd.DataFrame(rows.values(), columns=[self.API_DSName1], index=rows.keys())
        df = df.reset_index()
        df.rename(columns={'index': 'Date'}, inplace=True)
        df.dropna(axis=0, inplace=True)
        df["Date"] = pd.to_datetime(df['Date'])
        df.insert(1, 'Year', df.Date.dt.year)
        df.insert(2, 'Month', df.Date.dt.month)
        return df


    def get_averages(self, df):
        MthList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        MthList_upd = {i + 1: word for i, word in enumerate(MthList)}

        df = df.groupby(['Year', 'Month'], as_index=False).agg({self.API_DSName1: np.mean})
        df['Month'] = df['Month'].replace(MthList_upd)
        df.rename(columns={self.API_DSName1: f"{self.API_DSName1} Mean"}, inplace=True)
        return df


    def get_processed(self,df):
        MthList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        currency_1 = df.loc[:, self.API_DSName1]
        datas = [currency_1]
        for num, data in enumerate(datas):
            temp = []
            for i in range(0, len(data), 12):
                lists = data.iloc[i:i + 12, -1].values.tolist()
                temp.append(lists)
            datas[num] = pd.DataFrame(temp, columns=MthList, index=data.Year.unique().tolist()).round(3)
        datas = tuple(datas)
        return datas
    
   
