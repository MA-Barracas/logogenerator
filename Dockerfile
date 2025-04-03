# Usa una imagen base de Python oficial.
FROM python:3.9-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de dependencias primero para aprovechar el caché de Docker
COPY requirements.txt ./

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo
COPY . .

# Expone el puerto en el que Streamlit se ejecuta por defecto (y el que Cloud Run espera)
EXPOSE 8501

# Variable de entorno que Cloud Run usa para determinar en qué puerto escuchar.
ENV PORT=8501

# Comando para ejecutar la aplicación Streamlit cuando el contenedor se inicie.
# Escucha en todas las interfaces (0.0.0.0) y en el puerto especificado.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]