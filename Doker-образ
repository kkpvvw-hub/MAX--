# Используем официальный образ Python 3.12
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Указываем переменную окружения (токен будет передаваться при запуске)
ENV BOT_TOKEN=f9LHodD0cOIXvDof1IyrdJf5O9Zprvj65zpHZTTAKX28MZg7Syt46umwV3dQx80cePj645cceq0klaAjfDm7 - токен который был указан в качестве токена команды

# Запускаем бота
CMD ["python", "max_bot.py"]
