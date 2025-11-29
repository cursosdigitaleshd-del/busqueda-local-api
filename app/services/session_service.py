from typing import Optional, Dict
import time

class SessionService:
    def __init__(self):
        self.sessions = {}
        self.TTL = 300  # 5 minutos
        print("✓ Session Service inicializado (modo memoria)")

    async def guardar_sesion(self, chat_id: str, opciones: list, ciudad: str, barrio: str):
        """Guarda sesión de desambiguación"""
        self.sessions[chat_id] = {
            'opciones': opciones,
            'ciudad': ciudad,
            'barrio': barrio,
            'timestamp': time.time()
        }
        self._limpiar_sesiones_expiradas()

    async def obtener_sesion(self, chat_id: str) -> Optional[Dict]:
        """Obtiene sesión guardada"""
        self._limpiar_sesiones_expiradas()
        return self.sessions.get(chat_id)

    async def borrar_sesion(self, chat_id: str):
        """Borra sesión"""
        if chat_id in self.sessions:
            del self.sessions[chat_id]

    def _limpiar_sesiones_expiradas(self):
        """Limpia sesiones viejas"""
        now = time.time()
        expired = [k for k, v in self.sessions.items() if now - v['timestamp'] > self.TTL]
        for key in expired:
            del self.sessions[key]