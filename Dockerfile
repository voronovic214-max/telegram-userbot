# Используем официальный и стабильный образ Python 3.10
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код бота в контейнер
COPY . .

# Открываем порт, который будет слушать веб-сервер для Render
EXPOSE 8080

# Команда для запуска бота
CMD ["python", "userbot.py"]
