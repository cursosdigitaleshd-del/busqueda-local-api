import httpx
import csv
from io import StringIO
from typing import List, Dict, Optional
import time
from app.models.schemas import ValidacionCliente

class GoogleSheetsService:
    def __init__(self, spreadsheet_id_negocios: str):
        self.spreadsheet_id_negocios = spreadsheet_id_negocios
        self._cache_negocios = None
        self._cache_timestamp = 0
        self.CACHE_DURATION = 300
        print("✓ Google Sheets en modo público")

    async def leer_negocios(self) -> List[Dict]:
        try:
            if self._cache_negocios and (time.time() - self._cache_timestamp) < self.CACHE_DURATION:
                return self._cache_negocios
            
            url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id_negocios}/gviz/tq?tqx=out:csv"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code != 200:
                    print(f"Error leyendo Sheet: {response.status_code}")
                    return []
                
                csv_data = StringIO(response.text)
                reader = csv.DictReader(csv_data)
                negocios = list(reader)
                
                self._cache_negocios = negocios
                self._cache_timestamp = time.time()
                
                print(f"✓ Leídos {len(negocios)} negocios")
                return negocios
                
        except Exception as e:
            print(f"Error leyendo negocios: {e}")
            return []

    def _normalizar_telefono(self, telefono: str) -> str:
        telefono = str(telefono).strip()
        telefono = telefono.replace('+595', '').replace(' ', '').replace('-', '')
        if telefono.startswith('0'):
            telefono = telefono[1:]
        return telefono