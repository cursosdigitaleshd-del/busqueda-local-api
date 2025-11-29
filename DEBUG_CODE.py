"""
Sistema de Debug para API de Búsqueda Local
Agrega este código al inicio de la función buscar() en main.py
"""

# 🐛 MODO DEBUG: Activar escribiendo "debug" en Telegram
DEBUG_MODE = request.mensaje.lower().strip() == "debug"

if DEBUG_MODE:
    import os
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_NEGOCIOS_ID", "")
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    debug_msg = "🐛 **DEBUG MODE**\n\n"
    debug_msg += f"📊 **Variables de Entorno:**\n"
    debug_msg += f"• GOOGLE_SHEETS_NEGOCIOS_ID: {'✅ ' + spreadsheet_id[:20] + '...' if spreadsheet_id else '❌ NO CONFIGURADO'}\n"
    debug_msg += f"• OPENROUTER_API_KEY: {'✅ Configurado' if api_key else '❌ NO CONFIGURADO'}\n\n"
    
    # Test lectura de Google Sheets
    debug_msg += f"📖 **Test Google Sheets:**\n"
    try:
        negocios_test = await sheets_service.leer_negocios()
        debug_msg += f"• Total negocios: {len(negocios_test)}\n"
        if len(negocios_test) > 0:
            primer_negocio = negocios_test[0]
            debug_msg += f"• Primer negocio: {primer_negocio.get('NOMBRE COMERCIAL', primer_negocio.get('CONTACTO', 'Sin nombre'))}\n"
            debug_msg += f"• Rubros: {primer_negocio.get('RUBROSPRODUCTOS/SERVICIOS', 'Sin rubros')[:50]}...\n"
    except Exception as e:
        debug_msg += f"• ❌ Error: {str(e)}\n"
    
    # Test búsqueda
    debug_msg += f"\n🔍 **Test Búsqueda (plomero):**\n"
    try:
        negocios_test = await sheets_service.leer_negocios()
        resultados_test = search_service.buscar("plomero", negocios_test, "ASUNCION", "CENTRO", "Plan 2")
        debug_msg += f"• Resultados encontrados: {len(resultados_test)}\n"
        if len(resultados_test) > 0:
            debug_msg += f"• Primer resultado: {resultados_test[0].get('NOMBRE COMERCIAL', resultados_test[0].get('CONTACTO', 'Sin nombre'))}\n"
    except Exception as e:
        debug_msg += f"• ❌ Error: {str(e)}\n"
    
    # Test IA
    debug_msg += f"\n🤖 **Test IA:**\n"
    try:
        interpretacion_test = await ai_service.interpretar_mensaje("necesito un plomero", "ASUNCION", "CENTRO")
        debug_msg += f"• Tipo: {interpretacion_test.get('tipo', 'N/A')}\n"
        debug_msg += f"• Keyword: {interpretacion_test.get('keyword', 'N/A')}\n"
    except Exception as e:
        debug_msg += f"• ❌ Error: {str(e)}\n"
    
    return BusquedaResponse(
        tipo="saludo",
        mensaje=debug_msg,
        total_encontrados=0
    )
