import asyncio
import os
from app.services.sheets_service import GoogleSheetsService
from app.services.search_service import SearchService

# Configurar variables de entorno
os.environ["GOOGLE_SHEETS_NEGOCIOS_ID"] = "11V2aAAh9xhvEthUHaTx_Tnk4GfSyxdqt52jVUT4N92M"

async def test_search():
    # Inicializar servicios
    sheets_service = GoogleSheetsService(
        spreadsheet_id_negocios=os.getenv("GOOGLE_SHEETS_NEGOCIOS_ID", ""),
        spreadsheet_id_clientes=""
    )
    
    search_service = SearchService()
    
    # Leer negocios
    print("📊 Leyendo negocios de Google Sheets...")
    negocios = await sheets_service.leer_negocios()
    print(f"✓ Total negocios: {len(negocios)}\n")
    
    if len(negocios) > 0:
        print("📋 Primeros 3 negocios:")
        for i, neg in enumerate(negocios[:3], 1):
            print(f"\n{i}. {neg.get('NOMBRE COMERCIAL', neg.get('CONTACTO', 'Sin nombre'))}")
            print(f"   Rubros: {neg.get('RUBROSPRODUCTOS/SERVICIOS', 'Sin rubros')[:80]}...")
            print(f"   Ciudad: {neg.get('CIUDAD', 'Sin ciudad')}")
            print(f"   Teléfono: {neg.get('TELEFONO 1', 'Sin teléfono')}")
    
    # Probar búsquedas
    keywords = ["mecanico", "plomero", "electricista", "carpintero", "flete"]
    
    print("\n" + "="*60)
    print("🔍 PROBANDO BÚSQUEDAS")
    print("="*60)
    
    for keyword in keywords:
        print(f"\n🔎 Buscando: '{keyword}'")
        resultados = search_service.buscar(
            keyword,
            negocios,
            ciudad="ASUNCION",
            barrio="SAN VICENTE",
            plan="Plan 2"
        )
        print(f"   ✓ Resultados encontrados: {len(resultados)}")
        
        if len(resultados) > 0:
            for i, res in enumerate(resultados[:3], 1):
                nombre = res.get('NOMBRE COMERCIAL', res.get('CONTACTO', 'Sin nombre'))
                rubros = res.get('RUBROSPRODUCTOS/SERVICIOS', '')[:50]
                print(f"   {i}. {nombre} - {rubros}...")

if __name__ == "__main__":
    asyncio.run(test_search())
