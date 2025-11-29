# 🎯 CHEATSHEET - Comandos Útiles

## 🚀 SETUP INICIAL

```bash
# Conectar al VPS
ssh root@TU_VPS_IP

# Crear directorio
mkdir -p /opt/busqueda-local-api
cd /opt/busqueda-local-api

# Subir archivos (desde local)
scp busqueda-api.tar.gz root@TU_VPS_IP:/opt/busqueda-local-api/
tar -xzf busqueda-api.tar.gz

# Configurar .env
cp .env.example .env
nano .env

# Dar permisos a script
chmod +x setup.sh

# Ejecutar setup automático
./setup.sh
```

---

## 🐳 DOCKER

### Comandos Básicos

```bash
# Build
docker-compose build

# Iniciar
docker-compose up -d

# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Ver estado
docker-compose ps

# Ver logs (todos)
docker-compose logs -f

# Ver logs (solo API)
docker logs -f busqueda-local-api

# Ver logs (últimas 100 líneas)
docker logs --tail 100 busqueda-local-api
```

### Comandos Avanzados

```bash
# Rebuild forzado
docker-compose build --no-cache
docker-compose up -d --force-recreate

# Acceder al contenedor
docker exec -it busqueda-local-api /bin/bash

# Ver variables de entorno
docker exec busqueda-local-api env

# Ver uso de recursos
docker stats busqueda-local-api

# Limpiar todo (CUIDADO: borra volúmenes)
docker-compose down -v
docker system prune -a
```

---

## 🧪 TESTING

### Health Check

```bash
# Basic
curl http://localhost:8000/health

# Con detalles
curl -v http://localhost:8000/health

# Desde fuera del VPS
curl http://TU_DOMINIO:8000/health
```

### Test de Búsqueda

```bash
# Búsqueda simple
curl -X POST http://localhost:8000/api/buscar \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "Necesito un plomero",
    "chat_id": "test123",
    "telefono": "0981234567"
  }'

# Búsqueda genérica (debe pedir opciones)
curl -X POST http://localhost:8000/api/buscar \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "tengo hambre",
    "chat_id": "test456",
    "telefono": "0981234567"
  }'

# Selección numérica
curl -X POST http://localhost:8000/api/seleccion \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "test456",
    "opcion_numero": 2,
    "telefono": "0981234567"
  }'
```

### Test con jq (formato bonito)

```bash
# Instalar jq
apt-get install -y jq

# Usar
curl -s http://localhost:8000/health | jq .
curl -s -X POST http://localhost:8000/api/buscar \
  -H "Content-Type: application/json" \
  -d '{"mensaje":"plomero","chat_id":"x","telefono":"y"}' | jq .
```

---

## 🔍 DEBUGGING

### Ver Logs en Tiempo Real

```bash
# API
docker logs -f busqueda-local-api

# Redis
docker logs -f busqueda-redis

# Ambos
docker-compose logs -f

# Filtrar por palabra
docker logs busqueda-local-api 2>&1 | grep ERROR
docker logs busqueda-local-api 2>&1 | grep "Google Sheets"
```

### Verificar Conectividad

```bash
# Google Sheets
docker exec busqueda-local-api python3 -c "
from app.services.sheets_service import SheetsService
s = SheetsService()
print('Sheets connected:', s.is_connected())
"

# Redis
docker exec busqueda-redis redis-cli PING
# Debe retornar: PONG

# OpenRouter API
docker exec busqueda-local-api python3 -c "
import httpx, os
r = httpx.get('https://openrouter.ai/api/v1/models', 
  headers={'Authorization': f'Bearer {os.getenv(\"OPENROUTER_API_KEY\")}'})
print('Status:', r.status_code)
"
```

### Ver Variables de Entorno

```bash
# Todas
docker exec busqueda-local-api env

# Filtrar
docker exec busqueda-local-api env | grep GOOGLE
docker exec busqueda-local-api env | grep OPENROUTER
docker exec busqueda-local-api env | grep REDIS
```

---

## 📊 MONITOREO

### Uso de Recursos

```bash
# Tiempo real
docker stats

# Solo API
docker stats busqueda-local-api

# Snapshot
docker stats --no-stream
```

### Espacio en Disco

```bash
# Docker
docker system df

# VPS
df -h

# Logs size
du -sh /var/lib/docker/containers/*
```

### Cantidad de Requests

```bash
# Contar líneas de logs (aprox requests)
docker logs busqueda-local-api | grep "POST /api/buscar" | wc -l

# Últimos 10 requests
docker logs busqueda-local-api | grep "POST /api" | tail -10
```

---

## 🔧 MANTENIMIENTO

### Actualizar Código

```bash
# Opción A: Git pull
cd /opt/busqueda-local-api
git pull
docker-compose build
docker-compose up -d

# Opción B: Manual
# 1. Editar archivo
nano app/services/search_service.py
# 2. Rebuild
docker-compose build
docker-compose restart
```

### Limpiar Logs

```bash
# Truncar logs de Docker
truncate -s 0 $(docker inspect --format='{{.LogPath}}' busqueda-local-api)

# O configurar rotación en docker-compose.yml:
# logging:
#   driver: "json-file"
#   options:
#     max-size: "10m"
#     max-file: "3"
```

### Backup

```bash
# Backup de Redis
docker exec busqueda-redis redis-cli SAVE
docker cp busqueda-redis:/data/dump.rdb ./backup-$(date +%Y%m%d).rdb

# Backup de .env
cp .env .env.backup-$(date +%Y%m%d)

# Backup completo
tar -czf backup-$(date +%Y%m%d).tar.gz \
  .env \
  docker-compose.yml \
  app/
```

### Restaurar

```bash
# Restaurar Redis
docker cp ./backup-20250128.rdb busqueda-redis:/data/dump.rdb
docker restart busqueda-redis
```

---

## 🚨 TROUBLESHOOTING RÁPIDO

### API no responde

```bash
# 1. Ver logs
docker logs --tail 50 busqueda-local-api

# 2. Verificar que esté corriendo
docker ps | grep busqueda

# 3. Restart
docker restart busqueda-local-api

# 4. Si no inicia, rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Google Sheets no funciona

```bash
# Verificar credenciales
docker exec busqueda-local-api env | grep GOOGLE_CREDENTIALS_JSON

# Si está vacío o incorrecto:
nano .env
# Editar GOOGLE_CREDENTIALS_JSON
docker-compose restart
```

### Redis no funciona

```bash
# Verificar estado
docker ps | grep redis

# Si no está corriendo
docker-compose up -d redis

# Verificar conectividad
docker exec busqueda-redis redis-cli PING

# Ver logs
docker logs busqueda-redis
```

### Puerto 8000 ocupado

```bash
# Ver qué usa el puerto
sudo lsof -i :8000
# O
sudo netstat -tulpn | grep 8000

# Matar proceso
kill -9 PID

# O cambiar puerto en docker-compose.yml
# ports:
#   - "8001:8000"
```

---

## 🔄 ACTUALIZACIÓN DE VERSIÓN

```bash
# 1. Backup
tar -czf backup-before-update.tar.gz .

# 2. Pull cambios
git pull
# O subir archivos nuevos

# 3. Rebuild
docker-compose build --no-cache

# 4. Restart
docker-compose down
docker-compose up -d

# 5. Verificar
curl http://localhost:8000/health
docker logs -f busqueda-local-api
```

---

## 📱 COMANDOS PARA n8n

### Verificar workflow

```bash
# Desde n8n CLI (si está instalado)
n8n list:workflow

# Exportar workflow
n8n export:workflow --id=WORKFLOW_ID --output=workflow.json

# Importar workflow
n8n import:workflow --input=workflow.json
```

### Test de conexión API desde n8n

En nodo HTTP Request, agregar logging:

```javascript
// Pre-execute script
console.log('Enviando a API:', $json);

// Post-execute script  
console.log('Respuesta de API:', $json);
```

---

## 🎯 COMANDOS DE UN VISTAZO

```bash
# Quick health check
curl -s localhost:8000/health | jq .status

# Quick logs
docker logs --tail 20 busqueda-local-api

# Quick restart
docker restart busqueda-local-api

# Quick rebuild
docker-compose up -d --build --force-recreate

# Quick test
curl -X POST localhost:8000/api/buscar \
  -H "Content-Type: application/json" \
  -d '{"mensaje":"plomero","chat_id":"test","telefono":"123"}'
```

---

## 💾 SCRIPTS ÚTILES

### Script de monitoreo continuo

```bash
#!/bin/bash
# monitor.sh
while true; do
  clear
  echo "=== STATUS ==="
  docker ps | grep busqueda
  echo ""
  echo "=== HEALTH ==="
  curl -s localhost:8000/health | jq .
  echo ""
  echo "=== RESOURCES ==="
  docker stats --no-stream busqueda-local-api
  sleep 5
done
```

### Script de logs colored

```bash
#!/bin/bash
# logs.sh
docker logs -f busqueda-local-api 2>&1 | \
  grep --color=always -E "ERROR|WARNING|$"
```

---

**Guarda este archivo como referencia rápida.** 📚
