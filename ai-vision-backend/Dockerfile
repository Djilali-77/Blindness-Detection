# نستعملو نسخة بايثون خفيفة
FROM python:3.10-slim

# نحددو مسار العمل
WORKDIR /app

# هذي تاع مقبيل (تتفوت من الكاش)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# نكوبيو فايل المكتبات ونثبتوهم (تتفوت من الكاش وما تكلش الكونيكسيون)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🔥 العفسة تاعنا: نزيدو هذي هنا باش ما نكسروش الكاش تاع PyTorch 🔥
RUN apt-get update && apt-get install -y libgl1 && rm -rf /var/lib/apt/lists/*

# نكوبيو باقي الكود والأوزان
COPY . .

# نفتحو البورت 8000
EXPOSE 8000

# الكوماند لي تشعل السيرفر
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]