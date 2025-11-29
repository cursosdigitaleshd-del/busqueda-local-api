from rapidfuzz import fuzz
from typing import List, Dict
import unicodedata

class SearchService:
    def __init__(self):
        self.UMBRAL_SIMILITUD = 60
        self.UMBRAL_FALLBACK = 50
        self.MIN_KEYWORDS = 1
        self.MIN_SCORE = 40
        
        self.sinonimos = {
            'celular': ['telefono', 'movil', 'smartphone'],
            'telefono': ['celular', 'movil'],
            'flete': ['mudanza', 'transporte'],
            'mudanza': ['flete', 'transporte'],
            'mecanico': ['grua', 'taller'],
            'grua': ['mecanico', 'taller'],
        }

    def buscar(self, keyword: str, negocios: List[Dict], ciudad: str = "", barrio: str = "", plan: str = "Plan 1") -> List[Dict]:
        """Búsqueda principal con fuzzy matching"""
        keyword_norm = self._normalizar_texto(keyword)
        print(f"🔍 Buscando: '{keyword}' (normalizado: '{keyword_norm}')")
        print(f"📊 Total negocios: {len(negocios)}")
        print(f"📍 Ubicación: {ciudad}/{barrio}, Plan: {plan}")
        
        resultados = []
        debug_count = 0
        for negocio in negocios:
            # Filtrar por plan
            if plan == "Plan 1":
                neg_ciudad = self._normalizar_texto(negocio.get('CIUDAD', ''))
                if ciudad and neg_ciudad != self._normalizar_texto(ciudad):
                    continue
            
            rubros = self._normalizar_texto(negocio.get('RUBROSPRODUCTOS/SERVICIOS', ''))
            
            # Fuzzy matching
            score = fuzz.partial_ratio(keyword_norm, rubros)
            
            # Debug: mostrar primeros 3 negocios
            if debug_count < 3:
                print(f"  Negocio: {negocio.get('NOMBRE DEL NEGOCIO', 'Sin nombre')[:30]}")
                print(f"    Rubros: {rubros[:50]}")
                print(f"    Score: {score}")
                debug_count += 1
            
            # Bonus por ubicación
            if ciudad:
                neg_ciudad = self._normalizar_texto(negocio.get('CIUDAD', ''))
                neg_barrio = self._normalizar_texto(negocio.get('ZONA/BARRIO', ''))
                ciudad_norm = self._normalizar_texto(ciudad)
                barrio_norm = self._normalizar_texto(barrio)
                
                if neg_barrio == barrio_norm:
                    score += 300
                elif neg_ciudad == ciudad_norm:
                    score += 100
            
            if score >= self.MIN_SCORE:
                resultados.append({
                    'negocio': negocio,
                    'score': score
                })
        
        # Ordenar por score
        resultados.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ Encontrados {len(resultados)} resultados")
        if len(resultados) > 0:
            print(f"   Top score: {resultados[0]['score']}")
        
        return [r['negocio'] for r in resultados[:10]]

    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza texto para comparación"""
        texto = str(texto).lower()
        texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
        return texto