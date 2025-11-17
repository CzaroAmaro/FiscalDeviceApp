# 1. Użyj oficjalnego obrazu Node.js. Wersja 'alpine' jest bardzo mała.
FROM node:20-alpine

# 2. Ustaw katalog roboczy
WORKDIR /app

# 3. Skopiuj package.json i package-lock.json
COPY package*.json ./

# 4. Zainstaluj zależności
RUN npm install

# 5. Skopiuj resztę kodu aplikacji
COPY . .

# 6. Ustaw domyślną komendę uruchamiającą serwer deweloperski Vite
# Flaga '--host' jest kluczowa, aby serwer był dostępny z zewnątrz kontenera
CMD ["npm", "run", "dev", "--", "--host"]