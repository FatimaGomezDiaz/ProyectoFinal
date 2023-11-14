import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

a = Service(ChromeDriverManager().install())
opc = Options()
opc.add_argument("--window-size=700,620")
navegador = webdriver.Chrome(service=a, options=opc)
navegador.get("https://www.inegi.org.mx/sistemas/olap/proyectos/bd/continuas/mortalidad/defuncioneshom.asp?s=est&fbclid=IwAR1kKPjPPHvR-lfAfey1c9T2CjT8o0rSfKRmSpgPXYMjH-cyBNMwHEVUOtw")
