import httpx
import json
from typing import Dict, List, Optional

class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.0-flash-lite-preview-02-05:free"

    async def interpretar_mensaje(self, mensaje: str, ciudad: str, barrio: str) -> Dict:
        """Interpreta el mensaje del usuario usando IA"""
        try:
            prompt = self._construir_prompt(mensaje, ciudad, barrio)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code != 200:
                    print(f"Error AI API: {response.status_code}")
                    return self._fallback_interpretacion(mensaje)
                
                data = response.json()
                contenido = data['choices'][0]['message']['content']
                
                # Limpiar y parsear JSON
                contenido = contenido.strip()
                if contenido.startswith('```json'):
                    contenido = contenido[7:]
                if contenido.endswith('```'):
                    contenido = contenido[:-3]
                contenido = contenido.strip()
                
                resultado = json.loads(contenido)
                print(f"✓ IA interpretó: {resultado}")
                return resultado
                
        except Exception as e:
            print(f"Error en IA: {e}")
            return self._fallback_interpretacion(mensaje)

    def _construir_prompt(self, mensaje: str, ciudad: str, barrio: str) -> str:
        return f"""Eres un asistente que ayuda a interpretar búsquedas de negocios en Paraguay.

Usuario ubicado en: {ciudad}, {barrio}
Mensaje del usuario: "{mensaje}"

Categorías disponibles: electricista, plomero, carpintero, cerrajero, mecanico, pintor, albañil, gasista, vidrieria, herreria, aire acondicionado, instalacion electrica, reparacion celular, reparacion electrodomesticos, mudanza, flete, grua, taxi, remis, lavanderia, tintoreria, restaurante, almacen, panaderia, carniceria, verduleria, farmacia, veterinaria, peluqueria, barberia, estetica, gym, consultorio medico, abogado, contador, imprenta, libreria, ferreteria, repuestos auto, gomeria, lubricentro, estacion servicio.

Analiza el mensaje y responde SOLO con un JSON válido (sin texto adicional):

Si es específico (el usuario sabe qué busca):
{{"tipo": "busqueda", "keyword": "categoria_detectada", "ciudad": "{ciudad}", "barrio": "{barrio}"}}

Si es ambiguo (puede ser varias cosas):
{{"tipo": "ambiguo", "opciones": ["opcion1", "opcion2", "opcion3", "opcion4", "opcion5"]}}

Si es saludo o charla:
{{"tipo": "saludo"}}

Ejemplos:
- "necesito un plomero" → {{"tipo": "busqueda", "keyword": "plomero", "ciudad": "{ciudad}", "barrio": "{barrio}"}}
- "estoy sin luz" → {{"tipo": "busqueda", "keyword": "electricista", "ciudad": "{ciudad}", "barrio": "{barrio}"}}
- "quiero almorzar" → {{"tipo": "busqueda", "keyword": "restaurante", "ciudad": "{ciudad}", "barrio": "{barrio}"}}
- "servicio tecnico" → {{"tipo": "ambiguo", "opciones": ["electricista", "plomero", "mecanico", "reparacion celular", "reparacion electrodomesticos"]}}

Responde SOLO con JSON válido, nada más."""

    def _fallback_interpretacion(self, mensaje: str) -> Dict:
        """Fallback simple si IA falla"""
        mensaje_lower = mensaje.lower()
        
        keywords_directos = {
            'electricista': 'electricista', 'luz': 'electricista', 'electrico': 'electricista',
            'plomero': 'plomero', 'agua': 'plomero', 'cañeria': 'plomero',
            'carpintero': 'carpintero', 'madera': 'carpintero',
            'cerrajero': 'cerrajero', 'llave': 'cerrajero', 'cerradura': 'cerrajero',
            'mecanico': 'mecanico', 'auto': 'mecanico', 'coche': 'mecanico',
            'pintor': 'pintor', 'pintura': 'pintor',
            'restaurante': 'restaurante', 'almorzar': 'restaurante', 'comer': 'restaurante',
            'farmacia': 'farmacia', 'remedio': 'farmacia', 'medicamento': 'farmacia',
        }
        
        for key, value in keywords_directos.items():
            if key in mensaje_lower:
                return {"tipo": "busqueda", "keyword": value, "ciudad": "", "barrio": ""}
        
        return {
            "tipo": "ambiguo",
            "opciones": ["electricista", "plomero", "carpintero", "cerrajero", "mecanico"]
        }