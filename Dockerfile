FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY . .

# Создаем пользователя
RUN useradd -m -u 1000 flaskuser && \
    chown -R flaskuser:flaskuser /app

USER flaskuser

# Запускаем
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "app:app"]