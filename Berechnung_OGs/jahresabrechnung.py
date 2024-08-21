# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 23:11:16 2023

@author: proed
"""

import pandas as pd
pd.options.mode.copy_on_write = True
import functions

# Sollberechnung laden

soll = pd.read_excel('Sollberechnung/Saison_2023_2024/sollberechnung.xlsx',
                     index_col='V. Nr.') 
                     # usecols=['Verein','SR-Soll', 'Basis-OG pro SR-Fehl [€]'], 
                     # )

# Alle SR der abgelaufenen Saison laden (inkl. Aufhörer)

sr = pd.read_excel('2024 Q2/sr_saison_2023_2024.xlsx')
sr = sr.dropna(how='all')
sr['Soll-Status'] = sr['Soll-Status'].fillna('erfüllt')
sr['SR seit'] = pd.to_datetime(sr['SR seit'], format='%d.%m.%Y')

# sr['V. Nr.'] = sr['Vereinsnr.'].astype(int) + 21000000

# Aktive SR berechnen

files = {'Q3': '2023 Q3/Schiedsrichterstammdaten.xls',
         'Q4': '2023 Q4/Schiedsrichterstammdaten.xls',
         'Q1': '2024 Q1/Schiedsrichterstammdaten.xls',
         'Q2': '2024 Q2/Schiedsrichterstammdaten.xls'}

sr_aktiv = pd.DataFrame(index=soll.index)
sr_nicht_erfuellt = pd.DataFrame(index=soll.index)
sr_haertefall = pd.DataFrame(index=soll.index)

for label, file in files.items():
    # Stammdaten laden
    df = pd.read_excel(file, skiprows=2)
    df = df.dropna(subset='Vereinsnr.', how='all')
    df['V. Nr.'] = df['Vereinsnr.'].astype(int) + 21000000
    
    # Soll-Status hinzufügen
    df = df.merge(sr[['Ausweisnr.', 'Soll-Status']],
                  on='Ausweisnr.',
                  how='left')
    
    # Nach Verein gruppieren und auswerten
    g = df.groupby('V. Nr.')
    
    # Anzahl der aktiven SR berechnen
    sr_aktiv[label] = g.size()
    
    # Anzahl der SR, die ihr Soll nicht erfüllt haben
    sr_nicht_erfuellt[label] = g.apply(functions.count_soll_status,
                                       status='nicht erfüllt')
    
    # Anzahl der SR, die Härtefälle sind
    sr_haertefall[label] = g.apply(functions.count_soll_status,
                                   status='Härtefall')
    
sr_aktiv = sr_aktiv.fillna(0)
sr_nicht_erfuellt = sr_nicht_erfuellt.fillna(0)
sr_haertefall = sr_haertefall.fillna(0)

# Ursprüngliche OG-Berechnung durchführen

sr_fehl = -sr_aktiv.subtract(soll['SR-Soll'], axis='index')
sr_fehl = sr_fehl.map(lambda x: max(0, x))

ratio = sr_aktiv.divide(soll['SR-Soll'], axis='index')
ratio_faktor = (ratio < 0.595).replace({False: 1, True: 1.5})

og_pro_sr_fehl = ratio_faktor.multiply(soll['Basis-OG pro SR-Fehl [€]'], 
                                       axis='index')

og_abschlag = sr_fehl.multiply(og_pro_sr_fehl, axis='index')
og_abschlag['Q2'] = 0

# df_quartal = functions.quartalsbericht_erstellen(
#     'Q4', soll, sr_aktiv, sr_fehl, ratio, og_pro_sr_fehl, og_abschlag,
#     'Quartalsabrechnung_Q2_2024.xlsx')

# Neue SR für Bonus-Zahlungen bestimmen (betrifft nur Q2 weil letztes Quartal)

df['SR seit'] = pd.to_datetime(df['SR seit'], format='%d.%m.%Y')
df['neuer SR'] = df.apply(functions.neuer_sr, axis=1, stichtag='2021-07-01')

g = df.groupby('V. Nr.')

# Neue OG-Berechnung durchführen

sr_ist = sr_aktiv - sr_nicht_erfuellt
sr_fehl = -sr_ist.subtract(soll['SR-Soll'], axis='index')

bonus_überschuss = sr_fehl + sr_haertefall
bonus_überschuss = bonus_überschuss.map(lambda x: min(0, x))*100

sr_fehl = sr_fehl.map(lambda x: max(0, x))

ratio = sr_ist.divide(soll['SR-Soll'], axis='index')
ratio_faktor = (ratio < 0.595).replace({False: 1, True: 1.5})

og_pro_sr_fehl = ratio_faktor.multiply(soll['Basis-OG pro SR-Fehl [€]'], 
                                       axis='index')

og = sr_fehl.multiply(og_pro_sr_fehl, axis='index')
og['Q2'] = og['Q2'] + bonus_überschuss['Q2']

# Differenz zwischen ursprünglicher und neuer Soll-Berechnung

og_diff = og.subtract(og_abschlag)

# Ergebnisse zusammenfassen

df = soll[['Vereinsname', 'SR-Soll', 'Basis-OG pro SR-Fehl [€]']]
df['SR aktiv Q2'] = sr_aktiv['Q2']
df['SR-Ist Q2'] = sr_ist['Q2']
df['Härtefälle'] = sr_haertefall['Q2']
df['OG Q2 [€]'] = og_diff['Q2']
df['Nachzahlung SR unter Soll [€]'] = og_diff[['Q3', 'Q4', 'Q1']].sum(axis=1)
df['Anzahl neue SR'] = g['neuer SR'].sum()
df['Anzahl neue SR'] = df['Anzahl neue SR'].fillna(0)
df['neue SR'] = g.apply(functions.namen_neue_sr)
df['Bonus neue SR [€]'] = df.apply(functions.bonus_neue_sr, axis=1) # df['Anzahl neue SR']*(-200)
df['OG gesamt [€]'] = (df['OG Q2 [€]'] + 
                       df['Nachzahlung SR unter Soll [€]'] + 
                       df['Bonus neue SR [€]'])

# Ergebnisse sortieren und abspeichern

df = df.sort_values(['OG gesamt [€]', 'Vereinsname'])
print('Gesamtsumme: ', df['OG gesamt [€]'].sum())

with pd.ExcelWriter('jahresendabrechnung.xlsx') as writer:
    sr.to_excel(writer, sheet_name='Schiedsrichter', float_format="%.2f", index=False)
    df.to_excel(writer, sheet_name='Endabrechnung', float_format="%.2f")
    soll.to_excel(writer, sheet_name='Soll', float_format="%.2f")
    sr_aktiv.to_excel(writer, sheet_name='Aktive', float_format="%.2f")
    sr_nicht_erfuellt.to_excel(writer, sheet_name='Soll nicht erfüllt', float_format="%.2f")
    sr_haertefall.to_excel(writer, sheet_name='Härtefälle', float_format="%.2f")
    og_abschlag.to_excel(writer, sheet_name='Abschläge', float_format="%.2f")
    sr_ist.to_excel(writer, sheet_name='SR-Ist', float_format="%.2f")
    sr_fehl.to_excel(writer, sheet_name='SR-Fehl', float_format="%.2f")
    ratio.to_excel(writer, sheet_name='Soll-Ist-Verhältnis', float_format="%.2f")
    ratio_faktor.to_excel(writer, sheet_name='OG-Faktoren', float_format="%.2f")
    og_pro_sr_fehl.to_excel(writer, sheet_name='OGs pro SR-Fehl', float_format="%.2f")
    og.to_excel(writer, sheet_name='OGs neuberechnet', float_format="%.2f")
    og_diff.to_excel(writer, sheet_name='Neuberechnung minus Abschläge', float_format="%.2f")
    