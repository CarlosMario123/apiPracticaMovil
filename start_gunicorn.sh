#!/bin/bash

# Crear directorio para logs si no existe
mkdir -p logs

# Ejecutar Gunicorn como daemon
gunicorn \
    --bind 0.0.0.0:8000 \
    --worker-class uvicorn.workers.UvicornWorker \
    --daemon \
    --workers 4 \
    --pid gunicorn.pid \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    src.main:app

echo "Gunicorn iniciado en modo daemon. PID guardado en gunicorn.pid"
echo "Logs disponibles en:"
echo "  - logs/access.log"
echo "  - logs/error.log"
echo ""
echo "Para detener el servicio:"
echo "kill \$(cat gunicorn.pid)"