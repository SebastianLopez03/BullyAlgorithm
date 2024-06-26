# Usamos la imagen oficial de Python como base
FROM python:3.9-slim

# Definimos el directorio de trabajo en el contenedor
WORKDIR /

# Copiamos el código de la aplicación al contenedor
COPY . .

# Instalamos las dependencias del proyecto
RUN pip install --no-cache-dir Flask Flask-SocketIO pytz requests

# Exponemos el puerto 5000 para que Flask pueda escuchar las solicitudes
EXPOSE 5000

# Comando para ejecutar el programa NodeBully.py con los argumentos proporcionados
CMD ["python", "NodeBully.py"]
