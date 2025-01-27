#!/bin/bash


if [ ! -f "setup_project.py" ]; then
    echo "❌ El archivo setup_project.py no existe"
    exit 1
fi


if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi


echo "🚀 Ejecutando setup_project.py..."
python3 setup_project.py

if [ $? -eq 0 ]; then
    echo "✅ Estructura del proyecto creada exitosamente"
else
    echo "❌ Hubo un error al crear la estructura del proyecto"
    exit 1
fi
