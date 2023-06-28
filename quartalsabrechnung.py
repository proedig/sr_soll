# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 21:57:48 2022

@author: proed
"""

import pandas as pd

def og(row):
    if row['SR-Soll'] == 0: return row['Basis-OG pro SR-Fehl [€]']
    ratio = row['SR-Ist']/row['SR-Soll']
    if ratio < 0.6:
        return row['Basis-OG pro SR-Fehl [€]']*1.5
    else:
        return row['Basis-OG pro SR-Fehl [€]']


# Sollberechnung laden

soll = pd.read_excel('Sollberechnung2022_2023.xlsx')

# SR-Stammtdaten laden und gruppieren

sr = pd.read_excel('Schiedsrichterstammdaten.xls', skiprows=2)
sr = sr.dropna(how='all')

g = sr.groupby('Vereinsname')

ist = pd.DataFrame()
ist['SR-Ist'] = g['Name'].count()

# Soll und Ist vereinen

soll = soll[['Verein', 'SR-Soll', 'Basis-OG pro SR-Fehl [€]']]
df = soll.merge(ist, how='outer', left_on='Verein', right_index=True)

df['SR-Ist'] = df['SR-Ist'].fillna(0)
df['SR-Fehl'] = (df['SR-Soll'] - df['SR-Ist']).apply(lambda x: max(0, x))
df['Ist/Soll [%]'] =  df['SR-Ist']/df['SR-Soll']*100
df['OG pro SR-Fehl [€]'] = df.apply(og, axis=1)
df['OG [€]'] = (df['OG pro SR-Fehl [€]']*df['SR-Fehl']) # .round(2)

df = df.iloc[:, [0,1,3,4,5,2,6,7]]

df = df.sort_values(['OG [€]', 'Verein'])

df.to_excel('Quartalsabrechnung_2_2023.xlsx', index=False, float_format="%.2f")