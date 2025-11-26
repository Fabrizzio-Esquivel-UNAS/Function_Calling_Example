from typing import Optional
import jmespath
import requests
import json
import pydantic
from pydantic import BaseModel

# --- Modelos de Datos ---
# Define la estructura de un contacto usando Pydantic para validación de datos
class Contacto(BaseModel):
    id: Optional[int] = None
    nombre: str
    telefono: str
    email: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    fecha_nacimiento: Optional[str] = None

# Base de datos en un archivo JSON
DB_FILE = "database.json"

def leer_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def escribir_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def leer_contactos(expresion: str):
    """
    Ejecuta una consulta JMESPath en la base de datos de contactos.
    """
    contactos = leer_db()
    if not expresion:
        raise ValueError("La consulta no puede estar vacía")
    try:
        print("Ejecutando consulta JMESPath:", expresion)
        resultado = jmespath.search(expresion, contactos)
        return resultado
    except Exception as e:
        raise ValueError(f"Error en la consulta JMESPath: {str(e)}")

def actualizar_contacto(id_contacto, nuevos_datos):
    """
    Busca un contacto, mezcla los datos nuevos y valida todo con Pydantic antes de guardar.
    """
    contactos = leer_db()
    
    # Aseguramos que el ID sea un entero para la comparación
    try:
        id_buscado = int(id_contacto)
    except ValueError:
        print("El ID debe ser un número")
        return False

    for i, contacto_dict in enumerate(contactos):
        if contacto_dict.get('id') == id_buscado:
            # 1. Creamos una copia de los datos actuales para no dañar el original aún
            datos_mezclados = contacto_dict.copy()
            
            # 2. Aplicamos los cambios propuestos sobre la copia
            datos_mezclados.update(nuevos_datos)
            
            try:
                # 3. PASO CRÍTICO: Validación
                # Intentamos crear un objeto Contacto con los datos mezclados.
                # Si hay un error en los tipos de datos, Pydantic lanzará una excepción aquí.
                contacto_validado = Contacto(**datos_mezclados)
                
                # 4. Si la validación pasa, convertimos de nuevo a diccionario y guardamos
                # Nota: Usa .dict() si tienes Pydantic v1 o .model_dump() si es v2
                contactos[i] = contacto_validado.model_dump()
                
                escribir_db(contactos)
                print(f"Contacto {id_buscado} actualizado exitosamente.")
                return True
                
            except Exception as e:
                print(f"Error: Los nuevos datos no son válidos según el esquema Contacto.\nDetalle: {e}")
                return False

    print(f"No se encontró ningún contacto con el ID {id_buscado}")
    return False

def enviar_correo(destinatario: str, asunto: str, cuerpo: str):
    """
    Envía un correo electrónico.
    """
    print(f"Enviando correo a {destinatario} con asunto '{asunto}' y cuerpo '{cuerpo}'")
    
def obtener_horoscopo(timeframe: str, sign: str, day: str = "TODAY"):
    """
    Obtiene el horóscopo desde la API.
    timeframe: "daily", "weekly", or "monthly"
    sign: El signo del zodiaco
    day: "TODAY", "TOMORROW", "YESTERDAY", or a date in "YYYY-MM-DD" format (only for daily)
    """
    base_url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope"
    
    if timeframe not in ["daily", "weekly", "monthly"]:
        return {"error": "Timeframe no válido. Use 'daily', 'weekly', or 'monthly'."}
        
    endpoint = f"/{timeframe}"
    url = base_url + endpoint
    
    params = {"sign": sign}
    if timeframe == "daily":
        params["day"] = day
        
    try:
        print("Llamando a la API de horóscopos con URL:", url, "y parámetros:", params)
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lanza un error para respuestas 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Error al llamar a la API: {e}"}