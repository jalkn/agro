import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def run_automation():
    # 1. Load your local database
    local_data = pd.read_excel("database.xlsx")
    results = []

    async with async_playwright() as p:
        # Launch browser (headless=False lets you see the bot working)
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://sir.asocebu.com.co/Genealogias/")

        for index, row in local_data.iterrows():
            animal_id = str(row['Registration_Number'])
            
            # 2. Interact with the website
            # Note: You'll need to inspect the site for exact CSS selectors
            await page.fill('input[name="txtBusqueda"]', animal_id)
            await page.click('button#btnConsultar')
            
            # Wait for results to load
            await page.wait_for_timeout(2000) 

            # 3. Extraction Logic
            try:
                # Example: Grabbing the name from a specific table cell
                web_name = await page.inner_text('.result-table td.name')
                
                # Compare with local data
                status = "Match" if web_name == row['Local_Name'] else "Discrepancy"
                results.append({**row, "Web_Name": web_name, "Status": status})
            except:
                results.append({**row, "Web_Name": "Not Found", "Status": "Missing"})

        # 4. Save to Excel
        final_df = pd.DataFrame(results)
        final_df.to_excel("comparison_report.xlsx", index=False)
        
        await browser.close()
        print("Automation Complete! Check comparison_report.xlsx")

asyncio.run(run_automation())