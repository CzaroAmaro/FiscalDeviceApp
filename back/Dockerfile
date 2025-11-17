# 1. Użyj oficjalnego obrazu Python. Wersja 'slim' jest lżejsza.
FROM python:3.12

# 2. Ustaw zmienne środowiskowe
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Zainstaluj zależności systemowe dla WeasyPrint i MySQL client
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
          libpango-1.0-0 \
          libcairo2 \
          libpangoft2-1.0-0 \
          libffi-dev \
          pkg-config \
          default-libmysqlclient-dev \
          build-essential \
       && apt-get clean \
       && rm -rf /var/lib/apt/lists/*

# 4. Ustaw katalog roboczy w kontenerze
WORKDIR /app

# 5. Skopiuj plik z zależnościami i je zainstaluj
# Kopiowanie osobno pozwala Dockerowi na cache'owanie tej warstwy
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Skopiuj resztę kodu aplikacji do katalogu roboczego
COPY . .

# 7. Port, na którym będzie działać serwer deweloperski Django
EXPOSE 8000

# 8. Domyślna komenda do uruchomienia aplikacji (na potrzeby deweloperskie)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]