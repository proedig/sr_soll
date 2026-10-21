import pandas as pd

def og(row):
    if row['SR-Soll'] == 0: return row['Basis-OG pro SR-Fehl [€]']
    ratio = row['SR-Ist']/row['SR-Soll']
    if ratio < 0.595:
        return row['Basis-OG pro SR-Fehl [€]']*1.5
    else:
        return row['Basis-OG pro SR-Fehl [€]']

# Sollberechnung laden

soll = pd.read_excel('Sollberechnung/Saison_2026_2027/sollberechnung.xlsx')

# SR-Stammtdaten laden und gruppieren

sr = pd.read_excel('2026 Q3/sr-stammdaten.xlsx', skiprows=10)
sr = sr.dropna(how='all')

g = sr.groupby('Vereinsnummer')

ist = pd.DataFrame()
ist['SR-Ist'] = g.size()

# Soll und Ist vereinen
soll = soll[['Vereinsnummer', 'Vereinsname', 'SR-Soll', 'Basis-OG pro SR-Fehl [€]']]
df = soll.merge(ist, how='outer', left_on='Vereinsnummer', right_index=True)

df['SR-Ist'] = df['SR-Ist'].fillna(0)
df['SR-Fehl'] = (df['SR-Soll'] - df['SR-Ist']).apply(lambda x: max(0, x))
df['Ist/Soll'] =  df['SR-Ist']/df['SR-Soll']
df['OG pro SR-Fehl [€]'] = df.apply(og, axis=1)
df['OG [€]'] = (df['OG pro SR-Fehl [€]']*df['SR-Fehl']) # .round(2)

# Spalten umsortieren
df = df.iloc[:, [0,1,2,4,5,6,3,7,8]]

# Checken, ob Zuordnung nicht vollständig
if df["SR-Soll"].count() != len(df):
    print("Warnung: Nicht alle Schiedsrichter konnten einem Verein aus dem "
          "Dataframe 'soll' zugeordnet werden. Bitte Dataframe 'df' checken.")

df = df.sort_values(['OG [€]', 'Vereinsname'])

df.to_excel('Quartalsabrechnung_Q3_2026.xlsx', index=False, float_format="%.2f")