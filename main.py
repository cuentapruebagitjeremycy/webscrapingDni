from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright

app = FastAPI()

class Persona(BaseModel):
    nombres: str
    apellido_paterno: str
    apellido_materno: str

@app.get('/api/datos/dni', response_model=Persona)
async def scrapingDni(dni: str):
    async with async_playwright() as p:
        # Configurar navegador headless
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto("https://eldni.com")
            await page.fill("#dni", dni)
            await page.click("#btn-buscar-datos-por-dni")
            
            # Esperar a que los inputs estén listos
            await page.wait_for_selector("#apellidop", timeout=5000)
            
            apellido_paterno = await page.input_value("#apellidop") or "No disponible"
            apellido_materno = await page.input_value("#apellidom") or "No disponible"
            nombres = await page.input_value("#nombres") or "No disponible"
            
            return Persona(
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
        finally:
            await browser.close()