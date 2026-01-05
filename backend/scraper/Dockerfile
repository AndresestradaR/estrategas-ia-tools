FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Chromium para Playwright
RUN playwright install chromium

# Copiar código
COPY . .

# Ejecutar scraper
CMD ["python", "scraper_auto.py"]
