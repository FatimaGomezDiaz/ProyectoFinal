from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
import time

a = Service(ChromeDriverManager().install())
opc = Options()
opc.add_argument("--window-size=700,620")

data = []

years = [str(year) for year in range(2011, 2023)]

navegador = webdriver.Chrome(service=a, options=opc)
navegador.get("https://www.inegi.org.mx/temas/incidencia/")

time.sleep(5)

time.sleep(5)

entidades = navegador.find_elements(By.CLASS_NAME, "TdInicio")

for entidad in entidades:
    entidad_text = entidad.text.strip()

    if entidad_text.endswith("/1") or entidad_text.endswith("/2") or entidad_text.endswith("/3"):
        continue

    entidad_data = {"Entidad": entidad_text}
    entidad_datos = entidad.find_elements(By.XPATH, "following-sibling::td[@class='Td']")
    for i, tasa_element in enumerate(entidad_datos):
        if i < len(years):
            tasa_incidente_text = tasa_element.text.strip().replace(",", "")
            entidad_data[years[i]] = tasa_incidente_text

    data.append(entidad_data)

navegador.quit()

df = pd.read_csv("datasets/incidencia_delictiva_mexico.csv")
df = df.iloc[:-5]
df.to_csv("datasets/incidencia_delictiva_mexico.csv", index=False)
df = pd.read_csv("datasets/incidencia_delictiva_mexico.csv")




