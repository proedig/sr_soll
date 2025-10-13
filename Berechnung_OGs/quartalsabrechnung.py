# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 21:57:48 2022

@author: proed
"""

import pandas as pd

def og(row):
    if row['SR-Soll'] == 0: return row['Basis-OG pro SR-Fehl [€]']
    ratio = row['SR-Ist']/row['SR-Soll']
    if ratio < 0.595:
        return row['Basis-OG pro SR-Fehl [€]']*1.5
    else:
        return row['Basis-OG pro SR-Fehl [€]']


# Sollberechnung laden

soll = pd.read_excel('Sollberechnung/Saison_2025_2026/SR-Soll Saison 2025_2026.xlsx')

# SR-Stammtdaten laden und gruppieren

sr = pd.read_excel('2025 Q3/sr-stammdaten.xlsx', skiprows=10)
sr = sr.dropna(how='all')

g = sr.groupby('Vereinsnummer')

ist = pd.DataFrame()
ist['SR-Ist'] = g.size()

# Soll und Ist vereinen
soll = soll[['V. Nr.', 'Vereinsname', 'SR-Soll', 'Basis-OG pro SR-Fehl [€]']]
df = soll.merge(ist, how='outer', left_on='V. Nr.', right_index=True)

df['SR-Ist'] = df['SR-Ist'].fillna(0)
df['SR-Fehl'] = (df['SR-Soll'] - df['SR-Ist']).apply(lambda x: max(0, x))
df['Ist/Soll'] =  df['SR-Ist']/df['SR-Soll']
df['OG pro SR-Fehl [€]'] = df.apply(og, axis=1)
df['OG [€]'] = (df['OG pro SR-Fehl [€]']*df['SR-Fehl']) # .round(2)

# Spalten umsortieren
df = df.iloc[:, [0,1,2,4,5,6,3,7,8]]

# Checken, ob Zuordnung nicht vollständig
if df["SR-Soll"].count() != len(df):
    print("Warnung: Nicht alle Schiedsrichter konnten einem Verein aus dem "
          "Dataframe 'soll' zugeordnet werden. Bitte Dataframe 'df' checken.")

df = df.sort_values(['OG [€]', 'Vereinsname'])

df.to_excel('Quartalsabrechnung_Q3_2025.xlsx', index=False, float_format="%.2f")