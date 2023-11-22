from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
import time

# Configuración del driver
a = Service(ChromeDriverManager().install())
opc = Options()
opc.add_argument("--window-size=700,620")

# Configuración de datos
data = []

# Años predefinidos
years = [str(year) for year in range(2011, 2023)]

# Inicialización del navegador
navegador = webdriver.Chrome(service=a, options=opc)
navegador.get("https://www.inegi.org.mx/temas/incidencia/")

# Espera para asegurarse de que la página se haya cargado completamente
time.sleep(5)

# Esperar para que la nueva página cargue después de hacer clic en el enlace
time.sleep(5)

# Resto del script para obtener datos
entidades = navegador.find_elements(By.CLASS_NAME, "TdInicio")

for entidad in entidades:
    entidad_text = entidad.text.strip()

    # Si la entidad es una descripción de delito, la ignoramos
    if entidad_text.endswith("/1") or entidad_text.endswith("/2") or entidad_text.endswith("/3"):
        continue

    entidad_data = {"Entidad": entidad_text}

    # Encontrar los datos correspondientes a la entidad
    entidad_datos = entidad.find_elements(By.XPATH, "following-sibling::td[@class='Td']")

    # Procesar y agregar los datos al diccionario de la entidad
    for i, tasa_element in enumerate(entidad_datos):
        if i < len(years):
            tasa_incidente_text = tasa_element.text.strip().replace(",", "")
            entidad_data[years[i]] = tasa_incidente_text

    data.append(entidad_data)

# Cerrar el navegador
navegador.quit()

# Crear DataFrame y guardar datos en CSV
df = pd.DataFrame(data)
df.to_csv('datasets/incidencia_delictiva_mexico.csv', index=False)
print("Datos guardados en 'incidencia_delictiva_mexico.csv'")

