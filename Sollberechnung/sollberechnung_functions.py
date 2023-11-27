# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 23:16:42 2023

@author: proed
"""

import pandas as pd

def sr_per_team(row):
    match row['MS-Art'], row['Liga']:
        # Herren:
        case 'Herren', 'BL' | '2BL':
            return 4
        case 'Herren', '3BL' | 'RLW' | 'OLWFV' | 'VL' | 'LL':
            return 3
        case 'Herren', _:
            return 1
        # Frauen:
        case 'Frauen', 'BL' | '2BL' | 'RLW':
            return 3
        case 'Frauen', _:
            return 1
        # Jugend:
        case 'A-Junioren' | 'B-Junioren', 'BL':
            return 3
        case 'A-Junioren' | 'B-Junioren', 'VL':
            return 2
        case 'C-Junioren', 'RLW':
            return 1
        case 'B-Juniorinnen', 'BL' | 'RLW':
            return 1
        case 'A-Junioren' | 'B-Junioren', _:
            return 1
        # Sonstige:
        case _, 'BLCup' | 'AOL' | 'BzLAuf':
            msg = '{}: Liga "{}" kann nicht verarbeitet werden.'.format(
                row['Mannschaftsname'], row['Liga'])
            raise Exception(msg)
        case _:
            return 0


def og(row):
    match row['MS-Art'], row['Liga']:
        # Herren:
        case 'Herren', 'BL' | '2BL' | '3BL':
            return 125
        case 'Herren', 'RLW':
            return 112.5
        case 'Herren', 'OLWFV' | 'VL':
            return 100
        case 'Herren', 'LL' | 'BzL':
            return 75
        # Frauen:
        case 'Frauen', 'BL' | '2BL':
            return 100
        case 'Frauen', 'RLW':
            return 75
        # Sonstige:
        case _:
            return 62.50
        

def sr_per_team_2(group):
    ms_art = group['MS-Art'].iloc[0]
    spielklasse = group['Spielklasse'].iloc[0]
    team = group['Mannschaftsname'].iloc[0]
    anzahl_vereine = group['Verein'].nunique()
    match ms_art, spielklasse:
        case 'Herren', 'Kreisliga C':
            return 1/anzahl_vereine
        case 'Frauen', 'Kreisliga B':
            return 1/anzahl_vereine
        case 'A-Junioren' | 'B-Junioren', 'Kreisliga A':
            return 1/anzahl_vereine
        case 'C-Junioren', 'Kreisliga A':
            return 0
        case 'B-Juniorinnen' | 'C-Juniorinnen' | 'D-Junioren' | 'E-Junioren' | 'F-Junioren' | 'G-Junioren' | 'E-Juniorinnen', 'Kreisliga A':
            return 0
        case _:
            msg = '{}: Liga "{}" kann nicht verarbeitet werden.'.format(team, spielklasse)
            raise Exception(msg)
            
            
def is_spielgemeinschaft(row, ref):
    return (ref['Mannschaftsname'] == row['Mannschaftsname']).any()
    
            
def clubs_to_list(row):
    return [row['V. Nr.'], row['Ver. Nr. (Spg)']]


def og_per_club(group):
    herren = group[group['MS-Art'] == 'Herren']
    if len(herren) > 0:
        return herren['OG'].max() # Verein hat Herrenmannschaft
    else:
        return group['OG'].max() # Verein hat keine Herrenmannschaft
    
def relevant_teams(group):
    rel = group[group['SR'] > 0]
    if len(rel) == 0: return pd.NA
    rel = rel.sort_values('SR', ascending=False)
    text = rel.agg(lambda row: '{} {} ({} SR)'.format(row['Mannschaftsname'], 
                                                      row['MS-Art'],
                                                      round(row['SR'], 2)), axis=1)
    return text.str.cat(sep=', ')