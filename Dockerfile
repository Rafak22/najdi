# استخدام نسخة بايثون خفيفة
FROM python:3.10-slim

# تثبيت الأدوات الضرورية فقط (بدون gcc)
RUN apt-get update && \
    apt-get install -y ffmpeg libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# مجلد العمل
WORKDIR /app

# نسخ الملفات المهمة فقط (تجنب نسخ كل المشروع)
COPY main.py .
COPY server.py .
COPY model.py .
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# تشغيل الخادم
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]