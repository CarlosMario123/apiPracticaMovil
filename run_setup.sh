#!/bin/bash

# Verificar si el archivo setup_project.py existe
if [ ! -f "setup_project.py" ]; then
    echo "❌ El archivo setup_project.py no existe"
    exit 1
fi

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Ejecutar el script de Python
echo "🚀 Ejecutando setup_project.py..."
python3 setup_project.py

# Verificar si la ejecución fue exitosa
if [ $? -eq 0 ]; then
    echo "✅ Estructura del proyecto creada exitosamente"
else
    echo "❌ Hubo un error al crear la estructura del proyecto"
    exit 1
fi
