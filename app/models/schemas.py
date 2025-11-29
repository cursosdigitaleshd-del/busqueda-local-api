from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class BusquedaRequest(BaseModel):
    mensaje: str
    chat_id: str
    telefono: str

class SeleccionRequest(BaseModel):
    chat_id: str
    opcion: int

class ValidacionCliente(BaseModel):
    telefono: str
    ciudad: str
    barrio: str
    plan: str
    existe: bool

class BusquedaResponse(BaseModel):
    tipo: str
    mensaje: str
    resultados: Optional[List[Dict[str, Any]]] = None
    total_encontrados: int = 0
    requiere_seleccion: bool = False
    opciones: Optional[List[str]] = None