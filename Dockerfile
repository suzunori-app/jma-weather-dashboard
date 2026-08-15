FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# デフォルトはFlaskアプリの起動。テストを実行する場合は
# `docker run <image> pytest` のように上書きする。
CMD ["python", "app.py"]
