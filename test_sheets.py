import asyncio
import os
from app.services.sheets_service import GoogleSheetsService

async def test_sheets():
    # Test with the hardcoded ID directly
    sheet_id = "11V2aAAh9xhvEthUHaTx_Tnk4GfSyxdqt52jVUT4N92M"
    print(f"Testing with ID: {sheet_id}")
    
    service = GoogleSheetsService(sheet_id, "")
    negocios = await service.leer_negocios()
    
    print(f"Total negocios read: {len(negocios)}")
    if len(negocios) > 0:
        print("First business:", negocios[0])
    else:
        print("Failed to read businesses")

if __name__ == "__main__":
    asyncio.run(test_sheets())
