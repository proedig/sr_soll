# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 21:58:03 2023

@author: proed
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

# Schiedrichter laden

sr = pd.read_excel('Analyse/Schiedsrichterstammdaten.xls', skiprows=2)
sr = sr.dropna(how='all')
sr['SR seit'] = pd.to_datetime(sr['SR seit'], format='%d.%m.%Y')
sr['Geburtsdatum'] = pd.to_datetime(sr['Geburtsdatum'], format='%d.%m.%Y')
sr['Alter'] = (datetime.datetime(2023, 6, 30) - sr['Geburtsdatum'])/(
    pd.to_timedelta('365.25D'))
sr = sr[sr['SR seit'] <= '2022-07-01']



sr_ids = sr['Ausweisnr.'].unique()

# Spiele laden

df = pd.read_excel('Analyse/SpieleExport.xls', skiprows=2)
df = df.dropna(subset='Spielkennung:')

df['Spielkennung:'] = df['Spielkennung:'].astype(int)

gebiete = ['Deutschland', 'Region Westdeutschland', 'Kreis Münster',
           'Kreis Gütersloh', 'Kreis Dortmund', 'Kreis Ahaus-Coesfeld', 
           'Westfalen','Kreis Herne', 'Kreis Beckum', 'Bezirk Westfalen',
           'Kreis Steinfurt', 'Kreis Unna-Hamm']

#df = df[df['Spielgebiet'].isin(gebiete)]

spielstatus = ['Spiel anerkannt', 'Spiel erfolgt']

df = df[df['Spielstatus'].isin(spielstatus)]

# Pivot-Tabelle rückgängig

value_vars = ['(SR)Ausweisnummer', '(SRA1)Ausweisnummer', '(SRA2)Ausweisnummer',
              '(4.Off)Ausweisnummer', '(Pate)Ausweisnummer', ]

melt = df.melt('Spielkennung:', value_vars=value_vars, value_name='Ausweisnr.')
melt = melt[melt['Ausweisnr.'].isin(sr_ids)]

n_spiele = melt['Ausweisnr.'].value_counts()

sr2 = sr[['Ausweisnr.', 'Name', 'Vorname', 'Alter']].merge(
    n_spiele, how='left', left_on='Ausweisnr.', right_index=True)

sr2['count'] = sr2['count'].fillna(0)

bins = np.arange(-0.5, sr2['count'].max()+1, 1)
bins_age = np.arange(sr2['Alter'].min()-0.5, sr2['Alter'].max()+1, 1)

r = plt.hist(sr2['count'], bins=bins)
plt.axvline(x=15, label='15 Spiele', color='r', linestyle='dashed')
plt.xlabel('Anzahl Spiele in der Saison')
plt.ylabel('Anzahl Schiedsrichter')
plt.title('Saison 2022/2023')
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig('Analyse/spiele_je_sr.png', dpi=300)

# Namen hinzufügen

plt.figure()
r2 = plt.hist2d(sr2['count'], sr2['Alter'], bins=[bins, bins_age])
plt.axvline(x=15, label='15 Spiele', color='r', linestyle='dashed')
plt.xlabel('Anzahl Spiele in der Saison')
plt.ylabel('Alter Schiedsrichter')
plt.title('Saison 2022/2023')
plt.legend()
plt.colorbar(label='Anzahl SR', 
             ticks=np.arange(sr2['count'].max()))
plt.grid()
plt.tight_layout()
plt.savefig('Analyse/spiele_je_sr_vs_alter.png', dpi=300)