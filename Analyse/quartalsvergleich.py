# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 20:42:01 2023

@author: proed
"""

import pandas as pd

files = {'Q3 2022': '2022 Q3/Schiedsrichterstammdaten.xls',
         'Q4 2022': '2022 Q4/Schiedsrichterstammdaten.xls',
         'Q1 2023': '2023 Q1/Schiedsrichterstammdaten.xls',
         'Q2 2023': 'Schiedsrichterstammdaten.xls'}

v = pd.DataFrame()

for label, file in files.items():
    df = pd.read_excel(file, skiprows=2)
    df = df.dropna(how='all')
    g = df.groupby('Vereinsname')
    v[label] = g['Ausweisnr.'].count()
    # Einzelnen Verein betrachten
    df = df[df['Vereinsname'] == 'SC Münster 08']
    print(df['Name'].unique())
    
v['unverändert'] = v.eq(v.iloc[:, 0],axis=0).all(axis=1)