from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from app.models.schemas import BusquedaRequest, SeleccionRequest, BusquedaResponse
from app.services.sheets_service import GoogleSheetsService
from app.services.ai_service import AIService
from app.services.search_service import SearchService
from app.services.session_service import SessionService

app = FastAPI(title="Búsqueda Local API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar servicios
sheets_service = GoogleSheetsService(
    spreadsheet_id_negocios=os.getenv("GOOGLE_SHEETS_NEGOCIOS_ID", "")
)

# Leer API Key desde variable de entorno
env_api_key = os.getenv("OPENAI_API_KEY", "")

# Limpiar espacios
env_api_key = env_api_key.strip() if env_api_key else ""

# Inicializar servicio IA solo una vez
ai_service = AIService(api_key=env_api_key)

search_service = SearchService()
session_service = SessionService()

@app.get("/")
async def root():
    return {"message": "API de Búsqueda Local - OK"}

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "services": {
            "sheets": "ok",
            "sessions": "ok"
        }
    }

@app.post("/api/buscar", response_model=BusquedaResponse)
async def buscar(request: BusquedaRequest):
    """Endpoint principal de búsqueda"""
    try:
        # 1. Cliente default (sin validación - servicio público)
        from app.models.schemas import ValidacionCliente
        cliente = ValidacionCliente(
            telefono=request.telefono,
            ciudad="ASUNCION",  # Ciudad por defecto
            barrio="CENTRO",    # Barrio por defecto
            plan="Plan 2",      # Plan 2 = búsqueda nacional
            existe=True
        )
        
        # 2. Verificar si hay sesión activa
        sesion = await session_service.obtener_sesion(request.chat_id)
        if sesion:
            # 2.1 Verificar si el usuario quiere cancelar
            mensaje_lower = request.mensaje.lower().strip()
            if mensaje_lower in ['cancelar', 'cancel', 'salir', 'volver']:
                await session_service.borrar_sesion(request.chat_id)
                return BusquedaResponse(
                    tipo="saludo",
                    mensaje="✅ Selección cancelada. ¿Qué estás buscando?",
                    total_encontrados=0
                )
            
            # 2.2 Verificar si el mensaje es un número
            try:
                opcion_num = int(request.mensaje.strip())
                if 1 <= opcion_num <= len(sesion['opciones']):
                    # Procesar la selección
                    keyword = sesion['opciones'][opcion_num - 1]
                    negocios = await sheets_service.leer_negocios()
                    
                    resultados = search_service.buscar(
                        keyword,
                        negocios,
                        sesion['ciudad'],
                        sesion['barrio'],
                        cliente.plan
                    )
                    
                    # Borrar sesión después de procesar
                    await session_service.borrar_sesion(request.chat_id)
                    
                    if not resultados:
                        # Si no hay resultados, mostrar menú nuevamente
                        opciones_menu = ["electricista", "plomero", "carpintero", "cerrajero", "mecanico"]
                        await session_service.guardar_sesion(
                            request.chat_id,
                            opciones_menu,
                            cliente.ciudad,
                            cliente.barrio
                        )
                        
                        mensaje = f"😔 No encontré resultados para '{keyword}'.\n\n🔧 ¿Qué estás buscando?\n\n"
                        for i, opcion in enumerate(opciones_menu, 1):
                            mensaje += f"{i}️⃣ {opcion.capitalize()}\n"
                        mensaje += "\nResponde con el número o escribe 'cancelar' para volver."
                        
                        return BusquedaResponse(
                            tipo="ambiguo",
                            mensaje=mensaje,
                            requiere_seleccion=True,
                            opciones=opciones_menu
                        )
                    
                    mensaje = f"🏪 Encontré {len(resultados)} resultados para *{keyword}*:\n\n"
                    for i, neg in enumerate(resultados[:5], 1):
                        nombre = neg.get('NOMBRE DEL NEGOCIO', 'Sin nombre')
                        telefono = neg.get('TELEFONO', 'Sin teléfono')
                        ciudad = neg.get('CIUDAD', '')
                        barrio = neg.get('ZONA/BARRIO', '')
                        mensaje += f"{i}️⃣ *{nombre}*\n📞 {telefono}\n📍 {barrio}, {ciudad}\n\n"
                    
                    return BusquedaResponse(
                        tipo="resultados",
                        mensaje=mensaje,
                        resultados=resultados[:5],
                        total_encontrados=len(resultados)
                    )
            except ValueError:
                pass  # No es un número, continuar con mensaje de error
            
            # 2.3 Mensaje no válido durante selección
            return BusquedaResponse(
                tipo="ambiguo",
                mensaje=f"⏳ Tienes una selección pendiente.\n\nElige un número del 1 al {len(sesion['opciones'])} o escribe 'cancelar' para volver.",
                requiere_seleccion=True,
                opciones=sesion['opciones']
            )
        
        # 3. Interpretar mensaje con IA
        try:
            interpretacion = await ai_service.interpretar_mensaje(
                request.mensaje,
                cliente.ciudad,
                cliente.barrio
            )
        except Exception as e:
            print(f"⚠️ Error en IA, usando fallback: {e}")
            # Si la IA falla completamente, mostrar menú
            interpretacion = {
                "tipo": "ambiguo",
                "opciones": ["electricista", "plomero", "carpintero", "cerrajero", "mecanico"]
            }
        
        # 4. Procesar según tipo
        if interpretacion['tipo'] == 'saludo':
            return BusquedaResponse(
                tipo="saludo",
                mensaje="👋 ¡Hola! ¿Qué negocio o servicio estás buscando?",
                total_encontrados=0
            )
        
        elif interpretacion['tipo'] == 'ambiguo':
            opciones = interpretacion['opciones'][:5]
            await session_service.guardar_sesion(
                request.chat_id,
                opciones,
                cliente.ciudad,
                cliente.barrio
            )
            
            mensaje = "🔧 ¿Qué estás buscando?\n\n"
            for i, opcion in enumerate(opciones, 1):
                mensaje += f"{i}️⃣ {opcion.capitalize()}\n"
            mensaje += "\nResponde con el número o escribe 'cancelar' para volver."
            
            return BusquedaResponse(
                tipo="ambiguo",
                mensaje=mensaje,
                requiere_seleccion=True,
                opciones=opciones
            )
        
        else:  # busqueda
            keyword = interpretacion.get('keyword', request.mensaje)
            negocios = await sheets_service.leer_negocios()
            
            resultados = search_service.buscar(
                keyword,
                negocios,
                cliente.ciudad,
                cliente.barrio,
                cliente.plan
            )
            
            if not resultados:
                # Si no hay resultados, mostrar menú de opciones
                opciones_menu = ["electricista", "plomero", "carpintero", "cerrajero", "mecanico"]
                await session_service.guardar_sesion(
                    request.chat_id,
                    opciones_menu,
                    cliente.ciudad,
                    cliente.barrio
                )
                
                mensaje = f"😔 No encontré resultados para '{keyword}'.\n\n🔧 ¿Qué estás buscando?\n\n"
                for i, opcion in enumerate(opciones_menu, 1):
                    mensaje += f"{i}️⃣ {opcion.capitalize()}\n"
                mensaje += "\nResponde con el número o escribe 'cancelar' para volver."
                
                return BusquedaResponse(
                    tipo="ambiguo",
                    mensaje=mensaje,
                    requiere_seleccion=True,
                    opciones=opciones_menu
                )
            
            mensaje = f"🏪 Encontré {len(resultados)} resultados:\n\n"
            for i, neg in enumerate(resultados[:5], 1):
                nombre = neg.get('NOMBRE DEL NEGOCIO', 'Sin nombre')
                telefono = neg.get('TELEFONO', 'Sin teléfono')
                ciudad = neg.get('CIUDAD', '')
                barrio = neg.get('ZONA/BARRIO', '')
                mensaje += f"{i}️⃣ *{nombre}*\n📞 {telefono}\n📍 {barrio}, {ciudad}\n\n"
            
            return BusquedaResponse(
                tipo="resultados",
                mensaje=mensaje,
                resultados=resultados[:5],
                total_encontrados=len(resultados)
            )
        
    except Exception as e:
        print(f"Error en /api/buscar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/seleccion", response_model=BusquedaResponse)
async def seleccion(request: SeleccionRequest):
    """Procesa selección de usuario en desambiguación"""
    try:
        sesion = await session_service.obtener_sesion(request.chat_id)
        if not sesion:
            return BusquedaResponse(
                tipo="error",
                mensaje="❌ No hay selección pendiente. Realiza una nueva búsqueda.",
                total_encontrados=0
            )
        
        if request.opcion < 1 or request.opcion > len(sesion['opciones']):
            return BusquedaResponse(
                tipo="error",
                mensaje=f"❌ Opción inválida. Elige un número del 1 al {len(sesion['opciones'])}",
                total_encontrados=0
            )
        
        keyword = sesion['opciones'][request.opcion - 1]
        negocios = await sheets_service.leer_negocios()
        
        resultados = search_service.buscar(
            keyword,
            negocios,
            sesion['ciudad'],
            sesion['barrio']
        )
        
        await session_service.borrar_sesion(request.chat_id)
        
        if not resultados:
            return BusquedaResponse(
                tipo="sin_resultados",
                mensaje=f"😔 No encontré resultados para '{keyword}'",
                total_encontrados=0
            )
        
        mensaje = f"🏪 Encontré {len(resultados)} resultados:\n\n"
        for i, neg in enumerate(resultados[:5], 1):
            nombre = neg.get('NOMBRE DEL NEGOCIO', 'Sin nombre')
            telefono = neg.get('TELEFONO', 'Sin teléfono')
            ciudad = neg.get('CIUDAD', '')
            barrio = neg.get('ZONA/BARRIO', '')
            mensaje += f"{i}️⃣ *{nombre}*\n📞 {telefono}\n📍 {barrio}, {ciudad}\n\n"
        
        return BusquedaResponse(
            tipo="resultados",
            mensaje=mensaje,
            resultados=resultados[:5],
            total_encontrados=len(resultados)
        )
        
    except Exception as e:
        print(f"Error en /api/seleccion: {e}")
        raise HTTPException(status_code=500, detail=str(e))
