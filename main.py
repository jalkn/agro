import asyncio
import os
import sys
import pandas as pd
from playwright.async_api import async_playwright

# --- CONFIGURACIÓN PARA EL EJECUTABLE ---
# Esto obliga a Playwright a buscar los navegadores en la carpeta del bot
if getattr(sys, 'frozen', False):
    # Si estamos en el .exe
    bundle_dir = sys._MEIPASS
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(bundle_dir, "pw-browsers")
else:
    # Si estamos ejecutando el script .py normalmente
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

async def run_automation():
    print("Iniciando RPA Asocebu...")
    
    # 1. Cargar base de datos local
    try:
        local_data = pd.read_excel("database.xlsx")
        print(f"Cargados {len(local_data)} registros para procesar.")
    except Exception as e:
        print(f"Error: No se encontró 'database.xlsx'. {e}")
        return

    results = []

    async with async_playwright() as p:
        # Lanzar navegador (headless=False para que el cliente vea el proceso)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        for index, row in local_data.iterrows():
            animal_id = str(row['Registration_Number'])
            print(f"Consultando animal: {animal_id}")

            try:
                await page.goto("https://sir.asocebu.com.co/Genealogias/", timeout=60000)
                
                # Selector del cuadro de búsqueda (ajustar según inspección real)
                await page.fill('input[id*="txtBusqueda"]', animal_id)
                await page.keyboard.press("Enter")
                
                # Esperar a que la tabla o el mensaje de 'no resultados' aparezca
                await page.wait_for_timeout(3000) 

                # Lógica de extracción (ejemplo básico)
                # Aquí deberías capturar los selectores específicos de la tabla de Asocebu
                exists = await page.query_selector("table")
                
                if exists:
                    status = "Encontrado"
                    web_info = "Datos extraídos" # Aquí extraes el texto real
                else:
                    status = "No encontrado"
                    web_info = "N/A"

                results.append({**row, "Status_Web": status, "Info_Web": web_info})

            except Exception as e:
                print(f"Error procesando {animal_id}: {e}")
                results.append({**row, "Status_Web": "Error de conexión", "Info_Web": str(e)})

        # 2. Generar reporte final
        final_df = pd.DataFrame(results)
        final_df.to_excel("comparison_report.xlsx", index=False)
        print("Proceso finalizado. Reporte generado: comparison_report.xlsx")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_automation())