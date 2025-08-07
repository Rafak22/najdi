# استخدم نسخة بايثون خفيفة
FROM python:3.10-slim

# تثبيت بعض الأدوات الأساسية اللي slim ما تحتويها
RUN apt-get update && apt-get install -y gcc ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*

# إعداد مجلد العمل
WORKDIR /app

# نسخ ملفات المشروع
COPY . .

# تثبيت المتطلبات
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# تشغيل الخادم
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]