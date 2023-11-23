import pandas as pd

df = pd.read_csv("incidencia_delictiva_mexico.csv")
df = df.iloc[:-5]
df.to_csv("incidencia_delictiva_mexico_modificado.csv", index=False)


