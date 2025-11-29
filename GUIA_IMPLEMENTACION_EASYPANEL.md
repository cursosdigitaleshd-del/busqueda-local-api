# 🚀 GUÍA DE IMPLEMENTACIÓN - Paso a Paso en EasyPanel

## ✅ CHECKLIST PRE-IMPLEMENTACIÓN

Antes de empezar, asegúrate de tener:

- [ ] Acceso a tu VPS con EasyPanel instalado
- [ ] API Key de OpenRouter (https://openrouter.ai)
- [ ] Google Service Account con credenciales JSON
- [ ] IDs de tus Google Sheets (negocios y clientes)
- [ ] Google Sheets compartidos con el service account
- [ ] Telegram Bot Token (si usas Telegram)
- [ ] SSH access a tu VPS

---

## 📦 PASO 1: Preparar Credenciales

### 1.1 OpenRouter API Key

1. Ir a https://openrouter.ai
2. Sign up / Login
3. Settings → API Keys
4. Create new key
5. Copiar: `sk-or-v1-xxxxxxxxxxxxxxxx`

### 1.2 Google Service Account

1. Ir a https://console.cloud.google.com
2. Crear nuevo proyecto (o usar existente)
3. APIs & Services → Enable APIs → Google Sheets API
4. Credentials → Create Credentials → Service Account
5. Crear service account
6. Keys → Add Key → Create new key → JSON
7. Descargar el archivo JSON

### 1.3 Google Sheets

1. Abrir tu Google Sheet de negocios
2. URL: `https://docs.google.com/spreadsheets/d/[ID_AQUI]/edit`
3. Copiar el ID (entre `/d/` y `/edit`)
4. Share → Pegar email del service account (del JSON: `client_email`)
5. Dar permiso de "Viewer"
6. Repetir para sheet de clientes

---

## 📤 PASO 2: Subir Proyecto al VPS

### 2.1 Conectar al VPS

```bash
ssh root@TU_VPS_IP
```

### 2.2 Crear directorio

```bash
mkdir -p /opt/busqueda-local-api
cd /opt/busqueda-local-api
```

### 2.3 Subir archivos

**OPCIÓN A: Desde tu máquina local (recomendado)**

```bash
# En tu máquina local (donde descargaste los archivos)
cd busqueda-local-api
tar -czf busqueda-api.tar.gz .

# Subir al VPS
scp busqueda-api.tar.gz root@TU_VPS_IP:/opt/busqueda-local-api/

# En el VPS
ssh root@TU_VPS_IP
cd /opt/busqueda-local-api
tar -xzf busqueda-api.tar.gz
rm busqueda-api.tar.gz
```

**OPCIÓN B: Via Git (si tienes repositorio)**

```bash
cd /opt
git clone https://github.com/tu-usuario/busqueda-local-api.git
cd busqueda-local-api
```

---

## ⚙️ PASO 3: Configurar Variables de Entorno

### 3.1 Crear archivo .env

```bash
cd /opt/busqueda-local-api
cp .env.example .env
nano .env
```

### 3.2 Editar .env

```env
# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-tu-key-aqui

# Google Sheets
GOOGLE_SHEETS_NEGOCIOS_ID=1abc123def456  # Tu ID de negocios
GOOGLE_SHEETS_CLIENTES_ID=1xyz789uvw012  # Tu ID de clientes

# Google Credentials (copiar TODO el contenido del JSON, en UNA LÍNEA)
GOOGLE_CREDENTIALS_JSON='{"type":"service_account","project_id":"tu-proyecto","private_key_id":"abc123","private_key":"-----BEGIN PRIVATE KEY-----\nTU_CLAVE_COMPLETA_AQUI\n-----END PRIVATE KEY-----\n","client_email":"tu-email@tu-proyecto.iam.gserviceaccount.com","client_id":"123456","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/..."}' 

# Redis
REDIS_URL=redis://redis:6379
```

**IMPORTANTE**: 
- El JSON de Google debe estar en UNA sola línea
- Usar comillas simples para envolver el JSON
- Los `\n` en la private_key son literales, NO reemplazar

Guardar: `Ctrl+O` → Enter → `Ctrl+X`

---

## 🐳 PASO 4: Deploy en EasyPanel

### 4.1 Acceder a EasyPanel

1. Abrir: `https://tu-vps-ip:3000` (o tu dominio EasyPanel)
2. Login

### 4.2 Crear nuevo servicio

1. Click en **"Create Service"**
2. Tipo: **"Docker Compose"**
3. Nombre: `busqueda-local-api`

### 4.3 Configurar Docker Compose

Copiar y pegar el contenido de `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: /opt/busqueda-local-api
    container_name: busqueda-local-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - GOOGLE_SHEETS_NEGOCIOS_ID=${GOOGLE_SHEETS_NEGOCIOS_ID}
      - GOOGLE_SHEETS_CLIENTES_ID=${GOOGLE_SHEETS_CLIENTES_ID}
      - GOOGLE_CREDENTIALS_JSON=${GOOGLE_CREDENTIALS_JSON}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    networks:
      - busqueda-network

  redis:
    image: redis:7-alpine
    container_name: busqueda-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb
    volumes:
      - redis-data:/data
    networks:
      - busqueda-network

networks:
  busqueda-network:
    driver: bridge

volumes:
  redis-data:
```

### 4.4 Agregar Variables de Entorno

En EasyPanel, sección "Environment Variables":

```
OPENROUTER_API_KEY=sk-or-v1-tu-key
GOOGLE_SHEETS_NEGOCIOS_ID=1abc123
GOOGLE_SHEETS_CLIENTES_ID=1xyz789
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

### 4.5 Deploy

1. Click **"Deploy"**
2. Esperar 2-3 minutos
3. Ver logs en tiempo real

---

## ✅ PASO 5: Verificar Deployment

### 5.1 Health Check

```bash
curl http://localhost:8000/health

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

### 5.2 Test rápido

```bash
curl -X POST http://localhost:8000/api/buscar \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "Necesito un plomero",
    "chat_id": "test123",
    "telefono": "0981234567"
  }'
```

Debe retornar resultados o mensaje de desambiguación.

### 5.3 Ver logs

```bash
docker logs -f busqueda-local-api
```

---

## 🔧 PASO 6: Configurar n8n

### 6.1 Importar workflow simplificado

1. Abrir n8n
2. Ir a Workflows
3. **Import from file**
4. Seleccionar: `n8n-workflow-simplificado.json`

### 6.2 Configurar nodo HTTP Request

1. Abrir nodo **"Llamar API Python"**
2. Cambiar URL a: `http://busqueda-local-api:8000/api/buscar`
   - O si tienes dominio: `https://tu-api.com/api/buscar`
3. Verificar que Method sea `POST`
4. Verificar que Body esté en JSON

### 6.3 Probar workflow

1. Activar workflow
2. Enviar mensaje a tu bot de Telegram
3. Verificar respuesta

---

## 🔒 PASO 7: Configurar Dominio y SSL (Opcional)

### 7.1 En EasyPanel

1. Services → busqueda-local-api
2. **Add Domain**
3. Ingresar: `api.tu-dominio.com`
4. Enable SSL (Let's Encrypt)

### 7.2 Actualizar n8n

Cambiar URL en nodo HTTP Request:
```
https://api.tu-dominio.com/api/buscar
```

---

## 📊 PASO 8: Monitoreo

### 8.1 Ver logs en vivo

```bash
docker logs -f busqueda-local-api
docker logs -f busqueda-redis
```

### 8.2 Ver estado de contenedores

```bash
docker ps
```

### 8.3 Verificar uso de recursos

```bash
docker stats busqueda-local-api
```

---

## 🛠️ COMANDOS ÚTILES

```bash
# Reiniciar API
docker restart busqueda-local-api

# Ver logs de últimos 100 lines
docker logs --tail 100 busqueda-local-api

# Acceder al contenedor
docker exec -it busqueda-local-api /bin/bash

# Ver variables de entorno
docker exec busqueda-local-api env

# Rebuild y restart
cd /opt/busqueda-local-api
docker-compose build
docker-compose up -d

# Detener todo
docker-compose down

# Detener y limpiar volúmenes
docker-compose down -v
```

---

## 🐛 TROUBLESHOOTING

### Problema: "Google Sheets API not initialized"

**Síntomas**: API responde pero no encuentra clientes/negocios

**Solución**:
```bash
# Verificar credenciales
docker exec busqueda-local-api env | grep GOOGLE

# Si está vacío:
cd /opt/busqueda-local-api
nano .env
# Verificar que GOOGLE_CREDENTIALS_JSON esté en UNA línea
# Rebuild
docker-compose down
docker-compose up -d --build
```

### Problema: "AI service unavailable"

**Síntomas**: Búsquedas no funcionan, logs muestran error de OpenRouter

**Solución**:
```bash
# Verificar API key
docker exec busqueda-local-api env | grep OPENROUTER

# Verificar créditos en OpenRouter
# https://openrouter.ai/settings/billing
```

### Problema: "Redis connection failed"

**Síntomas**: Desambiguación no funciona, sesiones se pierden

**Solución**:
```bash
# Verificar que Redis esté corriendo
docker ps | grep redis

# Si no está:
docker-compose up -d redis

# Ver logs de Redis
docker logs busqueda-redis
```

### Problema: "Port 8000 already in use"

**Síntomas**: No puede iniciar, error de puerto

**Solución**:
```bash
# Ver qué usa el puerto
sudo lsof -i :8000

# Cambiar puerto en docker-compose.yml:
# ports:
#   - "8001:8000"  # Cambiar 8000 → 8001
```

---

## 📈 MÉTRICAS DE ÉXITO

Tu implementación es exitosa cuando:

✅ Health check retorna `"status": "healthy"`  
✅ Test de búsqueda retorna resultados  
✅ n8n recibe respuestas < 3 segundos  
✅ Logs no muestran errores  
✅ Usuarios pueden hacer búsquedas  
✅ Desambiguación funciona (sesiones persisten)  

---

## 🎉 ¡LISTO!

Tu API Python está corriendo y n8n está ultra-simplificado.

**Antes**: 25 nodos, difícil de mantener  
**Ahora**: 3 nodos, toda la lógica en Python

**Próximos pasos**:
1. Monitorear logs primeras 24 horas
2. Ajustar umbrales si es necesario
3. Agregar más sinónimos según casos reales
4. Configurar backups de Redis
5. Implementar rate limiting (opcional)

---

## 📞 SOPORTE

Si algo falla:
1. Ver logs: `docker logs busqueda-local-api`
2. Verificar health: `curl http://localhost:8000/health`
3. Revisar .env
4. Contactar soporte técnico

**¡Éxito con tu implementación!** 🚀
