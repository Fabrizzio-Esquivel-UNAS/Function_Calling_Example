# --- Importaciones ---
# Utilidades y funciones personalizadas
from utils import *
# Framework para la API
from fastapi import FastAPI, HTTPException
# Modelos de datos
from pydantic import BaseModel
# Para realizar peticiones HTTP
import requests
# Para manejar datos en formato JSON
import json
# Para consultas avanzadas en JSON
import jmespath
# Cliente de OpenAI
from openai import AsyncOpenAI
# Tipos de datos para anotaciones
from typing import List, Optional
# Definiciones de las funciones para OpenAI
from function_definitions import tools
# Servidor ASGI para FastAPI
import uvicorn
# Para cargar variables de entorno desde un archivo .env
from dotenv import load_dotenv
import os

# --- Configuración Inicial ---
# Carga las variables de entorno del archivo .env
load_dotenv()

# Configura la clave de la API de OpenAI desde las variables de entorno
aclient = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Crea una instancia de la aplicación FastAPI
app = FastAPI()

# Define la estructura para las peticiones al chat
class ChatRequest(BaseModel):
    prompt: str

# --- Diccionario de Funciones Disponibles ---
# Mapea los nombres de las funciones a las funciones reales para poder llamarlas dinámicamente
available_functions = {
    "enviar_correo": enviar_correo,
    "obtener_horoscopo": obtener_horoscopo,
    "actualizar_contacto": actualizar_contacto,
    "leer_contactos": leer_contactos,
}

# --- Endpoints de la API ---
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)

# Endpoint raíz para dar la bienvenida
@app.get("/")
def read_root():
    """Endpoint principal que devuelve un mensaje de bienvenida."""
    return {"message": "Bienvenido a la Agenda Telefónica"}

# Endpoint para crear un nuevo contacto
@app.post("/contactos", response_model=Contacto)
def crear_contacto(contacto: Contacto):
    """
    Crea un nuevo contacto en la base de datos.
    Asigna un ID único y lo guarda en el archivo JSON.
    """
    contactos = leer_db()
    if contactos:
        # Asigna un ID autoincremental
        contacto.id = max(c["id"] for c in contactos) + 1
    else:
        contacto.id = 1
    contactos.append(contacto.dict())
    escribir_db(contactos)
    return contacto

# Endpoint para obtener todos los contactos
@app.get("/contactos", response_model=List[Contacto])
def leer_contactos():
    """Devuelve la lista completa de contactos."""
    return leer_db()

# Endpoint para obtener un contacto por su ID
@app.get("/contactos/{contacto_id}", response_model=Contacto)
def leer_contacto(contacto_id: int):
    """
    Busca y devuelve un contacto específico por su ID.
    Si no lo encuentra, devuelve un error 404.
    """
    contactos = leer_db()
    for contacto in contactos:
        if contacto["id"] == contacto_id:
            return contacto
    raise HTTPException(status_code=404, detail="Contacto no encontrado")

# Endpoint para actualizar un contacto existente
@app.put("/contactos/{contacto_id}", response_model=Contacto)
def actualizar_contacto(contacto_id: int, contacto_actualizado: Contacto):
    """
    Actualiza los datos de un contacto existente por su ID.
    Si no lo encuentra, devuelve un error 404.
    """
    contactos = leer_db()
    for i, contacto in enumerate(contactos):
        if contacto["id"] == contacto_id:
            contacto_actualizado.id = contacto_id
            contactos[i] = contacto_actualizado.dict()
            escribir_db(contactos)
            return contacto_actualizado
    raise HTTPException(status_code=404, detail="Contacto no encontrado")

# Endpoint para eliminar un contacto
@app.delete("/contactos/{contacto_id}")
def eliminar_contacto(contacto_id: int):
    """
    Elimina un contacto de la base de datos por su ID.
    Si no lo encuentra, devuelve un error 404.
    """
    contactos = leer_db()
    contactos_filtrados = [c for c in contactos if c["id"] != contacto_id]
    if len(contactos_filtrados) == len(contactos):
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    escribir_db(contactos_filtrados)
    return {"message": "Contacto eliminado"}

@app.post("/chat")
async def chat_with_openai(request: ChatRequest):
    # Verifica que la clave de API esté configurada
    if not aclient.api_key:
        raise HTTPException(status_code=500, detail="La variable de entorno OPENAI_API_KEY no está configurada")

    messages = [{"role": "user", "content": request.prompt}]
    
    try:
        # Iniciamos el primer llamado
        response = await aclient.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message

        # BUCLE PRINCIPAL: Mientras el modelo quiera llamar a funciones, seguimos procesando
        while response_message.tool_calls:
            # 1. Agregamos la intención del asistente al historial
            messages.append(response_message)
            tool_calls = response_message.tool_calls
            
            # 2. Iteramos sobre las funciones solicitadas en este turno
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                
                if not function_to_call:
                    # En producción podrías manejar esto mejor, aquí retornamos error simple
                    return {"error": f"Función '{function_name}' no encontrada"}
                
                try:
                    print(f"Ejecutando: {function_name} args: {tool_call.function.arguments}")
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = function_to_call(**function_args)
                    
                    # 3. Agregamos el resultado de la función al historial
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(function_response),
                        }
                    )
                except Exception as e:
                    return {"error": f"Error en '{function_name}': {str(e)}"}

            # 4. Volvemos a llamar a OpenAI con los nuevos resultados en el historial
            # Esto permite que el modelo decida si necesita llamar a OTRA función (como update)
            # o si ya puede dar la respuesta final
            response = await aclient.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools, # Importante seguir enviando las herramientas disponibles
            )
            response_message = response.choices[0].message

        # Si llegamos aquí es porque response_message.tool_calls está vacío
        # y el modelo generó una respuesta de texto final
        return response_message

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar: {str(e)}")
    
# --- Ejecución de la Aplicación ---
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)