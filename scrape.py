from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

# URL objetivo
url = "https://www.sbs.gob.pe/app/pp/EstadisticasSAEEPortal/Paginas/TIPasivaMercado.aspx?tip=B"

# Configuración del navegador (modo headless para GitHub Actions o servidores)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Crear instancia del navegador
driver = webdriver.Chrome(service=Service(), options=options)

try:
    # Abrir URL
    driver.get(url)

    # Esperar que el contenido clave cargue
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "ctl00_cphContent_lblVAL_TIPMN_TASA"))
    )

    # Obtener HTML completo
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extraer tasas
    tipmn_span = soup.find("span", id="ctl00_cphContent_lblVAL_TIPMN_TASA")
    tipmex_span = soup.find("span", id="ctl00_cphContent_lblVAL_TIPMEX_TASA")

    if not tipmn_span or not tipmex_span:
        raise ValueError("No se pudieron encontrar los elementos de tasa.")

    tipmn = tipmn_span.text.strip()
    tipmex = tipmex_span.text.strip()

    # Crear DataFrame con los datos
    df = pd.DataFrame({
        "Moneda": ["Nacional (TIPMN)", "Extranjera (TIPMEX)"],
        "Tasa (%)": [tipmn, tipmex],
        "Periodo": ["Anual", "Anual"]
    })

    # Crear carpeta de salida con formato DATA/yyyy-mm-dd-SBS
    fecha = datetime.now().strftime("%Y-%m-%d")
    carpeta = os.path.join("DATA", f"{fecha}-SBS")
    os.makedirs(carpeta, exist_ok=True)

    # Guardar CSV
    salida = os.path.join(carpeta, "tasas_sbs.csv")
    df.to_csv(salida, index=False, encoding="utf-8-sig")

    print(f"✅ Datos guardados en: {salida}")
    print(df)

except Exception as e:
    print(f"❌ Ocurrió un error: {e}")

finally:
    driver.quit()
