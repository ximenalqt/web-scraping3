from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

# URL de la página
url = "https://www.sbs.gob.pe/app/pp/EstadisticasSAEEPortal/Paginas/TIPasivaMercado.aspx?tip=B"

# Configurar opciones para entorno sin cabeza (headless, útil para GitHub Actions)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Inicializa el navegador
service = Service()
driver = webdriver.Chrome(service=service, options=options)

# Cargar la página
driver.get(url)

try:
    # Esperar a que el contenido esté cargado
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "ctl00_cphContent_lblVAL_TIPMN_TASA"))
    )

    # Obtener HTML cargado
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Extraer valores
    tipmn = soup.find("span", id="ctl00_cphContent_lblVAL_TIPMN_TASA").text.strip()
    tipmex = soup.find("span", id="ctl00_cphContent_lblVAL_TIPMEX_TASA").text.strip()

    # Crear DataFrame
    df = pd.DataFrame({
        "Moneda": ["Nacional (TIPMN)", "Extranjera (TIPMEX)"],
        "Tasa (%)": [tipmn, tipmex],
        "Periodo": ["Anual", "Anual"]
    })

    # Crear carpeta con formato DATA/YYYY-MM-DD-SBS
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    carpeta = os.path.join("DATA", f"{fecha_hoy}-SBS")
    os.makedirs(carpeta, exist_ok=True)

    # Guardar CSV
    output_path = os.path.join(carpeta, "tasas_sbs.csv")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"✅ Datos guardados en: {output_path}")
    print(df)

except Exception as e:
    print("❌ Ocurrió un error:", e)

finally:
    driver.quit()
