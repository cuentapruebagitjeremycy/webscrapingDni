from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from fastapi import FastAPI
from pydantic import BaseModel

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

firefox_options = Options()
firefox_options.headless = True
firefox_options.add_argument("--headless")
firefox_options.add_argument("--disable-gpu")  # Opcional, ayuda a evitar errores gráficos en algunos casos
firefox_options.add_argument("--no-sandbox")  # Opcional, en algunos sistemas es necesario
driver = webdriver.Firefox(options=firefox_options)


app = FastAPI()

class AddHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["localtonet-skip-warningrequest"] = "true"
        return response

# Agregar el middleware a la app
app.add_middleware(AddHeaderMiddleware)


class Persona(BaseModel):
    nombres: str
    apellido_paterno: str
    apellido_materno: str


@app.get('/api/datos/dni', response_model=Persona)
async def scrapingDni(dni: str ):
    #navegamos a la web
    driver.get("https://eldni.com")
    #buscamos la caja de busqueda y escribimos el numero ed dni
    input_dni = driver.find_element(By.ID, "dni")
    input_dni.send_keys(dni)
    #buscamos el boton  y damos click para realizar la busqueda
    botton_buscar = driver.find_element(By.ID,"btn-buscar-datos-por-dni")
    botton_buscar.click()
    #driver.implicitly_wait(5)
    #sacamos los datos de cada input 
    input_apellido_paterno = driver.find_element(By.ID, "apellidop")
    input_apellido_materno = driver.find_element(By.ID, "apellidom")
    input_apellido_nombres = driver.find_element(By.ID, "nombres")

    # Obtenemos los valores de los inputs
    nombres = input_apellido_nombres.get_attribute("value") or "No disponible"
    apellido_paterno = input_apellido_paterno.get_attribute("value") or "No disponible"
    apellido_materno = input_apellido_materno.get_attribute("value") or "No disponible"

    # Crear una instancia de Persona
    persona = Persona(
        nombres=nombres,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno
    )

    return persona

# Cerrar el navegador cuando la aplicación se detenga
@app.on_event("shutdown")
def shutdown_event():
    driver.quit()