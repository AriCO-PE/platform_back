# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copiar y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Exponer el puerto de Django
EXPOSE 8000

# Comando para correr Django en producción
CMD ["gunicorn", "plataform_back.wsgi:application", "--bind", "0.0.0.0:8000"]
