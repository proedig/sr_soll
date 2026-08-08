# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 23:38:09 2024

@author: proed

Dieses Skript ermittelt die Schiedsrichter, die währende der Saison aufgehört
haben. Also die Schiedsrichter, die während der Saison irgendwann aktiv waren,
aber zum Saisonende (Q2) passiv sind.
"""

import pandas as pd

files = {'Q3': '2025 Q3/sr-stammdaten.xlsx',
         'Q4': '2025 Q4/sr-stammdaten.xlsx',
         'Q1': '2026 Q1/sr-stammdaten.xlsx',
         'Q2': '2026 Q2/sr-stammdaten.xlsx'}

dfs = []

for quartal, file in files.items():
    df = pd.read_excel(file, skiprows=10)
    df['Quartal'] = quartal
    dfs.append(df)
    
df = pd.concat(dfs)

# Pivot-Tabelle für Quartale erzeugen
pivot = df.pivot(columns='Quartal', 
                 index='Ausweisnummer',
                 values='Ausweisnummer')

pivot = pivot.notna().astype(int)

# Check, ob Vereinswechsel während der Saison stattgefunden haben
clubs = df.pivot(columns='Quartal', 
                 index='Ausweisnummer',
                 values='Vereinsname')

clubs["vereine"] = clubs.nunique(axis=1)

# Liste mit Ausweisnummer, Name und Vorname erzeugen
names = df[['Ausweisnummer', 'Nachname', 'Vorname', 'Soll-Status', 'Vereinsname', 'Vereinsnummer','SR seit']]
names = names.drop_duplicates(subset='Ausweisnummer', keep='last')
# names.to_excel('sr_saison_2025_2026.xlsx', index=False)
# names = names[['Ausweisnummer', 'Nachname', 'Vorname']]

# Name und Vorname ergänzen
pivot = pivot.merge(names, on='Ausweisnummer').sort_values(by=['Nachname', 'Vorname'])

# Spalten in richtige Reihenfolge bringen
pivot = pivot[['Ausweisnummer',
               'Nachname',
               'Vorname',
               'Soll-Status',
               'Vereinsname',
               'Vereinsnummer',
               'SR seit',
               'Q3',
               'Q4',
               'Q1',
               'Q2'
               ]]

pivot.to_excel('sr_saison_2025_2026.xlsx', index=False)

# Nur die Fälle betrachten, die jetzt (Q2) nicht mehr aktiv sind
relevant = pivot[pivot['Q2'] == 0]