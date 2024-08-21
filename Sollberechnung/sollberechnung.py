# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 12:09:37 2023

@author: proed
"""

import pandas as pd
import sollberechnung_functions as f
pd.options.mode.copy_on_write = True

# Fußball-Mannschaften aus Meldeliste einlesen
teams1 = pd.read_excel(
    'Sollberechnung/Saison_2024_2025/20240819_meldeliste.xls',
    skiprows=2)

# Futsal-Mannschaften aus Meldeliste einlesen
teams2 = pd.read_excel(
    'Sollberechnung/Saison_2024_2025/20240819_meldeliste (1).xls',
    skiprows=2)

# Beide Meldelisten vereinen
teams = pd.concat([teams1, teams2])

teams = teams.melt(id_vars=teams.columns[:10], var_name='Liga')
teams = teams.dropna(subset='value')
print('Anzahl Vereine:', teams['V. Nr.'].nunique())
        
teams['SR'] = teams.apply(f.sr_per_team, axis=1)
teams['OG'] = teams.apply(f.og, axis=1)

# Nach Verein gruppieren

g = teams.groupby('V. Nr.')

clubs = pd.DataFrame()
clubs['Vereinsname'] = g['Vereinsname'].first()
clubs['SR-Soll'] = g['SR'].sum()
clubs['Basis-OG pro SR-Fehl [€]'] = g.apply(f.og_per_club)
clubs['Relevante Mannschaften'] = g.apply(f.relevant_teams)    

# Ergebnisse speichern

with pd.ExcelWriter('sollberechnung.xlsx') as writer:  
    clubs.to_excel(writer, sheet_name='Sollberechnung', float_format="%.2f")
    teams.to_excel(writer, sheet_name='Mannschaften', index=False, 
                   float_format="%.2f")