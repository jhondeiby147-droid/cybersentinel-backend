# 1. Usar una imagen oficial de Python ligera pero robusta
FROM python:3.11-slim

# 2. Configurar variables de entorno para optimizar Python en contenedores
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalar dependencias del sistema operativo (necesarias para psycopg2 y librerías C)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Instalar 'uv', el gestor de paquetes ultrarrápido
RUN pip install uv

# 6. Copiar los archivos de configuración de tu proyecto
# (Si también generas un uv.lock, descomenta la siguiente línea)
COPY pyproject.toml ./
# COPY uv.lock ./ 

# 7. Instalar las dependencias leyendo el pyproject.toml directamente
RUN uv pip install --system -r pyproject.toml

# Si tu pyproject.toml no está configurado como un paquete instalable, usa esta alternativa:
# RUN uv pip install --system -r pyproject.toml

# 8. Copiar el resto del código fuente del backend al contenedor
COPY . .

# 9. Exponer el puerto que utilizará FastAPI
EXPOSE 8000

# 10. Comando de arranque del servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]