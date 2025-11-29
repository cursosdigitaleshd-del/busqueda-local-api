import asyncio
import os
from app.services.sheets_service import GoogleSheetsService
from app.services.search_service import SearchService

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
            print(f"\n{i}. {neg.get('NOMBRE DEL NEGOCIO', 'Sin nombre')}")
            print(f"   Rubros: {neg.get('RUBROSPRODUCTOS/SERVICIOS', 'Sin rubros')}")
            print(f"   Ciudad: {neg.get('CIUDAD', 'Sin ciudad')}")
    
    # Probar búsquedas
    keywords = ["mecanico", "plomero", "electricista", "carpintero"]
    
    print("\n" + "="*60)
    print("🔍 PROBANDO BÚSQUEDAS")
    print("="*60)
    
    for keyword in keywords:
        print(f"\n🔎 Buscando: '{keyword}'")
        resultados = search_service.buscar(
            keyword,
            negocios,
            ciudad="ASUNCION",
            barrio="CENTRO",
            plan="Plan 2"
        )
        print(f"   Resultados encontrados: {len(resultados)}")
        
        if len(resultados) > 0:
            print(f"   Primer resultado: {resultados[0].get('NOMBRE DEL NEGOCIO', 'Sin nombre')}")
    
    # Mostrar todos los rubros únicos
    print("\n" + "="*60)
    print("📊 RUBROS ÚNICOS EN LA BASE DE DATOS")
    print("="*60)
    rubros_set = set()
    for neg in negocios:
        rubros = neg.get('RUBROSPRODUCTOS/SERVICIOS', '')
        if rubros:
            rubros_set.add(rubros.lower().strip())
    
    rubros_list = sorted(list(rubros_set))[:20]  # Primeros 20
    for rubro in rubros_list:
        print(f"  - {rubro}")

if __name__ == "__main__":
    asyncio.run(test_search())
