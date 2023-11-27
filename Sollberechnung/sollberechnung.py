# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 12:09:37 2023

@author: proed
"""

import pandas as pd
import sollberechnung_functions as f
pd.options.mode.copy_on_write = True

# Spielgemeinschaften

teams2 = pd.read_excel('Saison_2023_2024/20230821_meldeliste_spielgemeinschaften.xls', skiprows=2)

teams2['Verein'] = teams2.apply(f.clubs_to_list, axis=1)
teams2 = teams2.explode('Verein')

team_id = ['Mannschaftsname', 'MS-Art', 'MS-Nr.', 'Spielklasse']
teams2 = teams2.drop_duplicates(subset=team_id + ['Verein'])

g = teams2.groupby(by=team_id, group_keys=False)

sr = g.apply(f.sr_per_team_2)
sr.name = 'SR'

teams2 = teams2.merge(sr, left_on=team_id, right_index=True)

g = teams2.groupby('Verein')

clubs2 = pd.DataFrame()
clubs2['SR-Soll'] = g['SR'].sum()
clubs2['Relevante Mannschaften'] = g.apply(f.relevant_teams)

# Normale Mannschaften

teams = pd.read_excel('Saison_2023_2024/20230820_meldeliste.xls', skiprows=2)

teams = teams.melt(id_vars=teams.columns[:8], var_name='Liga')
teams = teams.dropna()
print('Anzahl Vereine:', teams['V. Nr.'].nunique())

teams['Spielgemeinschaft'] = teams.apply(f.is_spielgemeinschaft, ref=teams2, axis=1)
teams = teams[~teams['Spielgemeinschaft']] # Spielgemeinschaften entfernen, damit sie nicht doppelt berücksichtigt werden
          
teams['SR'] = teams.apply(f.sr_per_team, axis=1)
teams['OG'] = teams.apply(f.og, axis=1)

# Nach Verein gruppieren

g = teams.groupby('V. Nr.')

clubs = pd.DataFrame()
clubs['Vereinsname'] = g['Vereinsname'].first()
clubs['SR-Soll'] = g['SR'].sum()
clubs['Basis-OG pro SR-Fehl [€]'] = g.apply(f.og_per_club)
clubs['Relevante Mannschaften'] = g.apply(f.relevant_teams)    

# Auswertungen für normale Mannschaften und Spielgemeinschaften zusammenführen

clubs['SR-Soll'] = clubs['SR-Soll'].add(clubs2['SR-Soll'], fill_value=0) 

my_join = lambda s1, s2: s1 + ', ' + s2 if pd.notna([s1, s2]).all() else (s1 or s2) 
clubs['Relevante Mannschaften'] = clubs['Relevante Mannschaften'].combine(clubs2['Relevante Mannschaften'], my_join)

# Ergebnisse speichern

with pd.ExcelWriter('sollberechnung.xlsx') as writer:  
    clubs.to_excel(writer, sheet_name='Sollberechnung', float_format="%.2f")
    teams.to_excel(writer, sheet_name='Mannschaften', index=False, float_format="%.2f")
    teams2.to_excel(writer, sheet_name='Spielgemeinschaften', index=False, float_format="%.2f")  