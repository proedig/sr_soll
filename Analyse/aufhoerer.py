# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 23:38:09 2024

@author: proed

Dieses Skript ermittelt die Schiedsrichter, die währende der Saison aufgehört
haben. Also die Schiedsrichter, die während der Saison irgendwann aktiv waren,
aber zum Saisonende (Q2) passiv sind.
"""

import pandas as pd

files = {'Q3': '2023 Q3/Schiedsrichterstammdaten.xls',
         'Q4': '2023 Q4/Schiedsrichterstammdaten.xls',
         'Q1': '2024 Q1/Schiedsrichterstammdaten.xls',
         'Q2': '2024 Q2/Schiedsrichterstammdaten.xls'}

dfs = []

for quartal, file in files.items():
    df = pd.read_excel(file, skiprows=2)
    df = df.dropna(subset='Vereinsnr.', how='all')
    df['Quartal'] = quartal
    dfs.append(df)
    
df = pd.concat(dfs)

# Pivot-Tabelle für Quartale erzeugen
pivot = df.pivot(columns='Quartal', 
                 index='Ausweisnr.',
                 values='Ausweisnr.')

pivot = pivot.notna().astype(int)

# Liste mit Ausweisnummer, Name und Vorname erzeugen
names = df[['Ausweisnr.', 'Name', 'Vorname', 'Vereinsname', 'SR seit']]
names = names.drop_duplicates(subset='Ausweisnr.', keep='last')
names.to_excel('sr_saison_2023_2024.xlsx', index=False)
names = names[['Ausweisnr.', 'Name', 'Vorname']]

# Name und Vorname ergänzen
pivot = pivot.merge(names, on='Ausweisnr.')

# Spalten in richtige Reihenfolge bringen
pivot = pivot[['Ausweisnr.', 'Name', 'Vorname', 'Q3', 'Q4', 'Q1', 'Q2']]

# Nur die Fälle betrachten, die jetzt (Q2) nicht mehr aktiv sind
relevant = pivot[pivot['Q2'] == 0]

