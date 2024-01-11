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

# Aktive SR berechnen

files = {'Q3': '2023 Q3/Schiedsrichterstammdaten.xls',
         'Q4': '2023 Q4/Schiedsrichterstammdaten.xls',
         'Q1': '2023 Q4/Schiedsrichterstammdaten.xls',
         'Q2': '2023 Q4/Schiedsrichterstammdaten.xls'}

sr_aktiv = pd.DataFrame(index=soll.index)

for label, file in files.items():
    df = pd.read_excel(file, skiprows=2)
    df = df.dropna(subset='Vereinsnr.', how='all')
    df['V. Nr.'] = df['Vereinsnr.'].astype(int) + 21000000
    g = df.groupby('V. Nr.')
    sr_aktiv[label] = g['Ausweisnr.'].count()
    
sr_aktiv = sr_aktiv.fillna(0)

# Ursprüngliche OG-Berechnung durchführen

sr_fehl = -sr_aktiv.subtract(soll['SR-Soll'], axis='index')
sr_fehl = sr_fehl.applymap(lambda x: max(0, x))

ratio = sr_aktiv.divide(soll['SR-Soll'], axis='index')
ratio_faktor = (ratio < 0.595).replace({False: 1, True: 1.5})

og_pro_sr_fehl = ratio_faktor.multiply(soll['Basis-OG pro SR-Fehl [€]'], 
                                       axis='index')

og_abschlag = sr_fehl.multiply(og_pro_sr_fehl, axis='index')
og_abschlag['Q2'] = 0

df_quartal = functions.quartalsbericht_erstellen(
    'Q4', soll, sr_aktiv, sr_fehl, ratio, og_pro_sr_fehl, og_abschlag,
    'Quartalsabrechnung_Q4_2023.xlsx')

# SR-Stammtdaten laden und gruppieren

sr = pd.read_excel(files['Q2'], skiprows=2)
sr = sr.dropna(how='all')
sr['Soll-Status'] = sr['Soll-Status'].fillna('erfüllt')
sr['SR seit'] = pd.to_datetime(sr['SR seit'], format='%d.%m.%Y')
sr['neuer SR'] = sr.apply(functions.neuer_sr, axis=1, stichtag='2020-07-01')
sr['V. Nr.'] = sr['Vereinsnr.'].astype(int) + 21000000

# SR nach Verein gruppieren und Kennzahlen berechnen

g = sr.groupby('V. Nr.')

ist = pd.DataFrame(index=soll.index)
ist['SR aktiv'] = g['Name'].count()
ist['davon Soll nicht erfüllt'] = g.apply(functions.count_soll_status, 
                                          status='nicht erfüllt')
ist['davon Härtefälle'] = g.apply(functions.count_soll_status, 
                                  status='Härtefall')
ist['SR unter Soll'] = g.apply(functions.sr_unter_soll)
ist['Anzahl neue SR'] = g['neuer SR'].sum()
ist['neue SR'] = g.apply(functions.namen_neue_sr)

ist = ist.fillna({'SR aktiv': 0,
                  'davon Soll nicht erfüllt': 0,
                  'davon Härtefälle': 0,
                  'Anzahl neue SR': 0})

ist['SR-Ist'] = ist['SR aktiv'] - ist['davon Soll nicht erfüllt']

# Neue OG-Berechnung durchführen

sr_ist = sr_aktiv.subtract(ist['davon Soll nicht erfüllt'], axis='index')
sr_fehl = -sr_ist.subtract(soll['SR-Soll'], axis='index')

bonus_überschuss = sr_fehl.add(ist['davon Härtefälle'], axis='index')
bonus_überschuss = bonus_überschuss.applymap(lambda x: min(0, x))*100

sr_fehl = sr_fehl.applymap(lambda x: max(0, x))

ratio = sr_ist.divide(soll['SR-Soll'], axis='index')
ratio_faktor = (ratio < 0.595).replace({False: 1, True: 1.5})

og_pro_sr_fehl = ratio_faktor.multiply(soll['Basis-OG pro SR-Fehl [€]'], 
                                       axis='index')

og = sr_fehl.multiply(og_pro_sr_fehl, axis='index')
og['Q2'] = og['Q2'] + bonus_überschuss['Q2']

# Differenz zwischen ursprünglicher und neuer Soll-Berechnung

og_diff = og.subtract(og_abschlag)

# Ergebnisse zusammenfassen

df = soll.copy()
df['SR aktiv'] = sr_aktiv['Q2']
df['davon Soll nicht erfüllt'] = ist['davon Soll nicht erfüllt']
df['davon Härtefälle'] = ist['davon Härtefälle']
df['SR unter Soll'] = ist['SR unter Soll']
df['SR-Ist'] = sr_ist['Q2']
df['SR-Fehl'] = df['SR-Soll'] - df['SR-Ist']
df['Ist/Soll [%]'] =  df['SR-Ist']/df['SR-Soll']*100
df['OG pro SR-Fehl [€]'] = og_pro_sr_fehl['Q2']
df['OG Q2 [€]'] = og_diff['Q2']
df['Nachzahlung SR unter Soll [€]'] = og_diff[['Q3', 'Q4', 'Q1']].sum(axis=1)
df['Anzahl neue SR'] = ist['Anzahl neue SR']
df['neue SR'] = ist['neue SR']
df['Bonus neue SR [€]'] = df.apply(functions.bonus_neue_sr, axis=1) # df['Anzahl neue SR']*(-200)
df['OG gesamt [€]'] = (df['OG Q2 [€]'] + 
                       df['Nachzahlung SR unter Soll [€]'] + 
                       df['Bonus neue SR [€]'])

# Ergebnisse sortieren und abspeichern

df = df.sort_values(['OG gesamt [€]', 'Vereinsname'])
print('Gesamtsumme: ', df['OG gesamt [€]'].sum())

#df.to_excel('jahresendabrechnung.xlsx', float_format="%.2f")

with pd.ExcelWriter('jahresendabrechnung.xlsx') as writer:  
    df.to_excel(writer, sheet_name='Endabrechnung', float_format="%.2f")
    soll.to_excel(writer, sheet_name='Soll', float_format="%.2f")
    sr_aktiv.to_excel(writer, sheet_name='Aktive', float_format="%.2f")
    og_abschlag.to_excel(writer, sheet_name='Abschläge', float_format="%.2f")
    ist.to_excel(writer, sheet_name='SR unter Soll', float_format="%.2f")
    sr_ist.to_excel(writer, sheet_name='SR-Ist', float_format="%.2f")
    sr_fehl.to_excel(writer, sheet_name='SR-Fehl', float_format="%.2f")
    ratio.to_excel(writer, sheet_name='Soll-Ist-Verhältnis', float_format="%.2f")
    ratio_faktor.to_excel(writer, sheet_name='OG-Faktoren', float_format="%.2f")
    og_pro_sr_fehl.to_excel(writer, sheet_name='OGs pro SR-Fehl', float_format="%.2f")
    og.to_excel(writer, sheet_name='OGs neuberechnet', float_format="%.2f")
    og_diff.to_excel(writer, sheet_name='Neuberechnung minus Abschläge', float_format="%.2f")
    