# استخدام نسخة خفيفة من Python
FROM python:3.10-slim

# تثبيت المكتبات الضرورية فقط
RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل
WORKDIR /app

# نسخ الملفات الأساسية فقط
COPY main.py .
COPY server.py .
COPY model.py .
COPY requirements.txt .
COPY .env .

# تثبيت المتطلبات
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# تشغيل التطبيق واستخدام منفذ بيئة التشغيل
CMD ["uvicorn", "main:app, "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]