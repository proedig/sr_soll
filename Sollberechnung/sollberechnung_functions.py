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
        case 'Herren', 'BzL' | 'KLA' | 'KLB' | 'KLC' | 'FRL':
            return 1
        case 'Herren', 'FVL':
            return 0
        # Frauen:
        case 'Frauen', 'BL' | '2BL' | 'RLW':
            return 3
        case 'Frauen', 'VL' | 'LL' | 'BzL' | 'KLA' | 'KLB':
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
        case _, 'Ki':
            return 0
        case ('B-Juniorinnen'
              | 'C-Junioren'
              | 'C-Juniorinnen'
              | 'D-Junioren'
              | 'D-Juniorinnen'
              | 'E-Junioren' 
              | 'E-Juniorinnen' 
              | 'B-Juniorinnen', 
              _):
            return 0
        # Altherren
        case 'Herren Ü60' | 'Herren Ü50' | 'Herren Ü40' | 'Herren Ü32', _:
            return 0
        # Sonstige:
        case _, 'WFKLA':
            return 0
        case _, _:
            msg = '{}: {} mit Liga "{}" kann nicht verarbeitet werden.'.format(
                row['Mannschaftsname'], row['MS-Art'], row['Liga'])
            raise Exception(msg)
        # case _:
        #     return 0


def og(row):
    match row['MS-Art'], row['Liga']:
        # Herren:
        case 'Herren', 'BL' | '2BL' | '3BL':
            return 125
        case 'Herren', 'RLW':
            return 112.5
        case 'Herren', 'OLWFV' | 'VL' | 'FBL':
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
    
            
def clubs_to_list(row):
    return [row['V. Nr.'], row['Ver. Nr. (Spg)']]


def og_per_club(group):
    herren = group[group['MS-Art'] == 'Herren']
    
    # Verein hat Herrenmannschaft
    if len(herren) > 0:
        return herren['OG'].max()
    # Verein hat keine Herrenmannschaft
    else:
        return group['OG'].max() 
    
def relevant_teams(group):
    rel = group[group['SR'] > 0]
    if len(rel) == 0: return pd.NA
    rel = rel.sort_values('SR', ascending=False)
    text = rel.agg(
        lambda row: '{} {} ({} SR)'.format(row['Mannschaftsname'], 
                                           row['MS-Art'],
                                           round(row['SR'], 2)), axis=1)
    return text.str.cat(sep=', ')