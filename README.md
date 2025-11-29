# 🔍 Búsqueda Local API

API FastAPI para búsqueda de negocios locales con IA y fuzzy matching.

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Telegram/     │
│   WhatsApp      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     n8n         │ (3 nodos)
│  - Trigger      │
│  - HTTP Request │
│  - Send Message │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  FastAPI (Python)           │
│  ┌─────────────────────┐    │
│  │ /api/buscar         │    │
│  │ /api/seleccion      │    │
│  └─────────────────────┘    │
│  ┌─────────────────────┐    │
│  │ - AI Service        │    │
│  │ - Search Service    │    │
│  │ - Sheets Service    │    │
│  │ - Session Service   │    │
│  └─────────────────────┘    │
└─────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Google Sheets  │
│  Redis          │
│  OpenRouter     │
└─────────────────┘
```

## 📦 Estructura del Proyecto

```
busqueda-local-api/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app principal
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Modelos Pydantic
│   └── services/
│       ├── __init__.py
│       ├── ai_service.py        # Llama 3.1 (OpenRouter)
│       ├── search_service.py    # Fuzzy search (RapidFuzz)
│       ├── sheets_service.py    # Google Sheets
│       └── session_service.py   # Redis/Memory
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Instalación en EasyPanel

### Paso 1: Preparar credenciales

1. **OpenRouter API Key**:
   - Regístrate en https://openrouter.ai
   - Crea una API key
   - Copia: `sk-or-v1-xxxxxxxxxx`

2. **Google Sheets**:
   - Google Cloud Console → Crear Service Account
   - Descargar JSON de credenciales
   - Compartir tus Sheets con el email del service account
   - Copiar IDs de tus Sheets (desde la URL)

3. **Configurar `.env`**:
   ```bash
   cp .env.example .env
   nano .env
   ```
   
   Completar:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-tu-key-aqui
   GOOGLE_SHEETS_NEGOCIOS_ID=tu-id-sheet-negocios
   GOOGLE_SHEETS_CLIENTES_ID=tu-id-sheet-clientes
   GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
   REDIS_URL=redis://redis:6379
   ```

### Paso 2: Subir a tu VPS

```bash
# En tu máquina local
cd busqueda-local-api
tar -czf busqueda-local-api.tar.gz .

# Subir al VPS
scp busqueda-local-api.tar.gz root@TU_VPS_IP:/root/

# En el VPS
ssh root@TU_VPS_IP
cd /root
tar -xzf busqueda-local-api.tar.gz -C /opt/busqueda-local-api
cd /opt/busqueda-local-api
```

### Paso 3: Desplegar en EasyPanel

**OPCIÓN A: Via Docker Compose (recomendado)**

1. En EasyPanel, crear nuevo servicio "Docker Compose"
2. Pegar el contenido de `docker-compose.yml`
3. Agregar variables de entorno desde `.env`
4. Deploy

**OPCIÓN B: Via Dockerfile**

1. EasyPanel → New Service → Docker
2. Repository: tu repositorio git (o subir código)
3. Dockerfile path: `./Dockerfile`
4. Port: `8000`
5. Environment variables: copiar desde `.env`
6. Deploy

### Paso 4: Verificar deployment

```bash
# Health check
curl http://TU_DOMINIO:8000/health

# Debe retornar:
{
  "status": "healthy",
  "services": {
    "sheets": "ok",
    "ai": "ok",
    "sessions": "ok"
  }
}
```

## 🔧 Configurar n8n

### Workflow simplificado (3 nodos)

```
1. Telegram/WhatsApp Trigger
   ↓
2. HTTP Request (POST a API)
   ↓
3. Send Message
```

### Nodo 2: HTTP Request

**URL**: `https://tu-api.com/api/buscar`

**Method**: `POST`

**Body** (JSON):
```json
{
  "mensaje": "{{ $json.message.text }}",
  "chat_id": "{{ $json.message.chat.id }}",
  "telefono": "{{ $json.message.from.phone_number }}"
}
```

**Headers**:
```
Content-Type: application/json
```

### Nodo 3: Send Message

**Chat ID**: `{{ $json.chat_id }}`

**Text**: `{{ $('HTTP Request').first().json.mensaje }}`

---

## 📡 API Endpoints

### `POST /api/buscar`

Endpoint principal de búsqueda.

**Request**:
```json
{
  "mensaje": "Necesito un plomero urgente",
  "chat_id": "123456789",
  "telefono": "0981234567"
}
```

**Response** (resultados encontrados):
```json
{
  "tipo": "resultados",
  "mensaje": "🏪 Encontré 3 resultados:\n\n1️⃣ Juan Pérez...",
  "resultados": [
    {
      "NOMBRE COMERCIAL": "Juan Pérez",
      "TELEFONO 1": "0981234567",
      "CIUDAD": "ASUNCION",
      "ZONA/BARRIO": "SAN VICENTE",
      "RUBROSPRODUCTOS/SERVICIOS": "PLOMERO, PLOMERIA"
    }
  ],
  "total_encontrados": 3,
  "requiere_seleccion": false
}
```

**Response** (requiere desambiguación):
```json
{
  "tipo": "ambiguo",
  "mensaje": "🔧 ¿Qué estás buscando exactamente?\n\n1️⃣ Electricista\n2️⃣ Plomero...",
  "resultados": [],
  "requiere_seleccion": true,
  "opciones": ["electricista", "plomero", "cerrajero"]
}
```

### `POST /api/seleccion`

Maneja selección numérica del usuario.

**Request**:
```json
{
  "chat_id": "123456789",
  "opcion_numero": 2,
  "telefono": "0981234567"
}
```

**Response**: Mismo formato que `/api/buscar`

### `GET /health`

Health check del sistema.

**Response**:
```json
{
  "status": "healthy",
  "services": {
    "sheets": "ok",
    "ai": "ok",
    "sessions": "ok"
  }
}
```

---

## 🧪 Testing Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# Correr API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# En otra terminal, probar
curl -X POST http://localhost:8000/api/buscar \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "Necesito un plomero",
    "chat_id": "test123",
    "telefono": "0981234567"
  }'
```

---

## 🐳 Docker

```bash
# Build
docker build -t busqueda-local-api .

# Run
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name busqueda-api \
  busqueda-local-api

# Logs
docker logs -f busqueda-api

# Stop
docker stop busqueda-api
```

O con docker-compose:

```bash
# Iniciar todo (API + Redis)
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

---

## 📊 Monitoreo

### Logs

```bash
# Docker
docker logs -f busqueda-api

# EasyPanel
Via dashboard de EasyPanel → Logs tab
```

### Métricas clave

- **Latencia**: < 2 segundos por búsqueda
- **Caché Google Sheets**: 5 minutos
- **Sesiones TTL**: 5 minutos
- **Redis Memory**: Max 256MB

---

## 🔒 Seguridad

- ✅ Variables de entorno para secrets
- ✅ CORS configurado para n8n
- ✅ Health checks
- ✅ Rate limiting (TODO)
- ✅ Redis password (configurar en producción)

---

## 🐛 Troubleshooting

### Error: "Google Sheets API not initialized"

**Solución**:
1. Verificar que `GOOGLE_CREDENTIALS_JSON` esté configurado
2. O que `GOOGLE_CREDENTIALS_PATH` apunte al archivo correcto
3. Verificar permisos del Service Account en Google Sheets

### Error: "Redis connection failed"

**Solución**:
1. Verificar que Redis esté corriendo: `docker ps | grep redis`
2. Verificar `REDIS_URL` en `.env`
3. Si no tienes Redis, la API usa memoria (funciona pero no persiste)

### Error: "AI service unavailable"

**Solución**:
1. Verificar `OPENROUTER_API_KEY`
2. Verificar créditos en OpenRouter
3. Ver logs para detalles: `docker logs busqueda-api`

---

## 📈 Ventajas vs n8n puro

| Aspecto | n8n puro | Python API |
|---------|----------|------------|
| **Complejidad** | 25+ nodos | 3 nodos n8n |
| **Debugging** | Difícil | Breakpoints normales |
| **Versionado** | JSON gigante | Git normal |
| **Tests** | No | Sí (pytest) |
| **Performance** | Overhead | Optimizado |
| **Librerías** | Limitadas | Cualquiera (RapidFuzz) |
| **Mantenimiento** | Alto | Bajo |

---

## 🚀 Próximas mejoras

- [ ] Rate limiting por usuario
- [ ] Logging estructurado (Sentry)
- [ ] Tests automatizados (pytest)
- [ ] CI/CD (GitHub Actions)
- [ ] Webhooks para actualizar caché
- [ ] Analytics dashboard
- [ ] Multi-idioma
- [ ] Geolocalización GPS

---

## 📝 Licencia

MIT

---

## 💬 Soporte

Para dudas o problemas, abre un issue o contacta al equipo de desarrollo.
