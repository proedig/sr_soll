# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 20:37:31 2023

@author: proed
"""

import pandas as pd
pd.options.mode.copy_on_write = True
import datetime

def og_pro_sr_fehl(row):
    if row['SR-Soll'] == 0: return row['Basis-OG pro SR-Fehl [€]']
    ratio = row['SR-Ist']/row['SR-Soll']
    if ratio < 0.595:
        return row['Basis-OG pro SR-Fehl [€]']*1.5
    else:
        return row['Basis-OG pro SR-Fehl [€]']


def anzahl_sr_unter_soll(group):
    counts = group['Soll-Status'].value_counts()
    if len(counts) > 3: 
        raise ValueError("Spalte 'Soll-Status' hat mehr als drei Werte. Habe nur die Werte 'erfüllt', 'nicht erfüllt' oder 'Härtefall' erwartet.")
    try:
        return counts['nicht erfüllt']
    except KeyError:
        return 0
    
    
def count_soll_status(group, status):
    counts = group['Soll-Status'].value_counts()
    try:
        return counts[status]
    except KeyError:
        return 0
    

def sr_unter_soll(group):
    group = group[group['Soll-Status'] == 'nicht erfüllt']
    new_name = group['Name'].combine(group['SR seit'], 
                                     lambda x,y: '{} ({})'.format(x,y.date()))
    #names = group['Name'].to_list()
    names = new_name.to_list()
    return str.join(', ', names)


def og(row):
    if row['SR-Fehl'] > 0:
        return row['SR-Fehl']*row['OG pro SR-Fehl [€]']
    else:
        return row['SR-Fehl']*100


def nachzahlung(row):
    # Nachzahlung für die SR unter Soll
    if row['SR-Fehl'] > 0:
        nachzahlung = (row[['davon Soll nicht erfüllt', 'SR-Fehl']].min()*
                       row['OG pro SR-Fehl [€]']*3)
    else:
        nachzahlung = 0
    # Nachzahlung für die SR über dem Soll aufgrund 60%-Regelung
    # sr_fehl_alt = row['SR-Soll'] - row['SR aktiv']
    # if row['SR-Soll'] == 0:
    #     nachzahlung2 = 0
    # elif sr_fehl_alt <= 0:
    #     nachzahlung2 = 0
    # elif ((row['SR aktiv']/row['SR-Soll'] >= 0.6) and 
    #     (row['SR-Ist']/row['SR-Soll'] < 0.6)):
    #         nachzahlung2 = sr_fehl_alt*row['Basis-OG pro SR-Fehl [€]']*0.5*3
    #         print(row['Verein'], nachzahlung2)
    # else:
    #     nachzahlung2 = 0     
    return nachzahlung


def neuer_sr(row, stichtag):
    # SR hat sein Soll nicht erfüllt:
    if row['Soll-Status'] != 'erfüllt':
        return False
    # SR ist noch nicht seit 2 Jahren Schiedsrichter:
    now = datetime.datetime.now()
    if row['SR seit'].replace(year=row['SR seit'].year+2) > now:
        return False 
    # Bonus wurde für den SR in der Vergangenheit schon berechnet:
    stichtag = pd.to_datetime(stichtag)
    if row['SR seit'] >= stichtag:
        return True
    else:
        return False
    
    
def bonus_neue_sr(row):
    """Gibt den Bonus für neue SR in Euro zurück."""
    if row['SR-Ist Q2'] > row['SR-Soll']:
        return row['Anzahl neue SR']*(-200)
    else:
        return 0
    
    
def namen_neue_sr(group):
    group = group[group['neuer SR']]
    new_name = group['Name'].combine(group['SR seit'], 
                                     lambda x,y: '{} ({})'.format(x,y.date()))
    # names = group['Name'].to_list()
    names = new_name.to_list()
    return str.join(', ', names)


def quartalsbericht_erstellen(quartal, soll, sr_aktiv, sr_fehl, ratio, 
                              og_pro_sr_fehl, og_abschlag,
                              output_file):
    df = soll[['Vereinsname', 'SR-Soll', 'Basis-OG pro SR-Fehl [€]']]
    df['SR-Ist'] = sr_aktiv[quartal]
    df['SR-Fehl'] = sr_fehl[quartal]
    df['Ist/Soll [%]'] = ratio[quartal]*100
    df['OG pro SR-Fehl [€]'] = og_pro_sr_fehl[quartal]
    df['OG [€]'] = og_abschlag[quartal]
    df = df.iloc[:, [0,1,3,4,5,2,6,7]]
    df = df.sort_values(['OG [€]', 'Vereinsname'])
    df.to_excel(output_file, float_format="%.2f")
    return df
    