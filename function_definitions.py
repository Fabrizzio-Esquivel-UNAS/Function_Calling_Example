tools = [
    {
        "type": "function",
        "function": {
            "name": "leer_contactos",
            "description": "Lee contactos de la base de datos ejecutando una consulta JMESPath. Útil para filtrar, buscar u ordenar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expresion": {
                        "type": "string",
                        "description": "La cadena de expresión JMESPath para realizar la consulta."
                    }
                },
                "required": ["expresion"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_contacto",
            "description": "Actualiza la información de un contacto existente usando su ID y un objeto con los nuevos datos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_contacto": {
                        "type": "integer",
                        "description": "El ID numérico único del contacto a editar."
                    },
                    "nuevos_datos": {
                        "type": "object",
                        "description": "Objeto con los campos a actualizar del contacto.",
                        "properties": {
                            "nombre": {
                                "type": "string",
                                "description": "Nombre completo del contacto."
                            },
                            "telefono": {
                                "type": "string",
                                "description": "Número de teléfono."
                            },
                            "email": {
                                "type": "string",
                                "description": "Correo electrónico."
                            },
                            "direccion": {
                                "type": "string",
                                "description": "Dirección física."
                            },
                            "ciudad": {
                                "type": "string",
                                "description": "Ciudad de residencia."
                            },
                            "pais": {
                                "type": "string",
                                "description": "País de residencia."
                            },
                            "fecha_nacimiento": {
                                "type": "string",
                                "description": "Fecha de nacimiento en formato YYYY-MM-DD."
                            }
                        },
                        "additionalProperties": False
                    }
                },
                "required": ["id_contacto", "nuevos_datos"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "enviar_correo",
            "description": "Envía un correo electrónico a un destinatario específico con un asunto y cuerpo definidos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destinatario": {
                        "type": "string",
                        "description": "La dirección de correo electrónico del destinatario."
                    },
                    "asunto": {
                        "type": "string",
                        "description": "El asunto o título del correo."
                    },
                    "cuerpo": {
                        "type": "string",
                        "description": "El contenido principal o mensaje del correo electrónico."
                    }
                },
                "required": ["destinatario", "asunto", "cuerpo"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_horoscopo",
            "description": "Obtiene el horóscopo actual o futuro para un signo zodiacal específico mediante una API externa.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeframe": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly"],
                        "description": "El periodo de tiempo para el horóscopo."
                    },
                    "sign": {
                        "type": "string",
                        "description": "El signo del zodiaco en inglés. Ejemplo: aries, libra, scorpio."
                    },
                    "day": {
                        "type": "string",
                        "description": "Solo para timeframe diario. Puede ser TODAY, TOMORROW, YESTERDAY o una fecha YYYY-MM-DD. Por defecto es TODAY."
                    }
                },
                "required": ["timeframe", "sign"],
                "additionalProperties": False
            }
        }
    }
]