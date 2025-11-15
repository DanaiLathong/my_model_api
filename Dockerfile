# 1. ใช้ Base Image ที่มี Python
FROM python:3.10-slim

# 2. สร้างพื้นที่ทำงานในกล่อง
WORKDIR /code

# 3. คัดลอกไฟล์ requirements.txt เข้าไปก่อน
COPY requirements.txt .

# 4. ติดตั้ง Library ที่จำเป็น
RUN pip install --no-cache-dir -r requirements.txt

# 5. คัดลอกโฟลเดอร์ app และ models ของเราเข้าไปในกล่อง
COPY ./app /code/app
COPY ./models /code/models

# 6. บอก Docker ว่า API ของเราจะรันที่ Port 8080
EXPOSE 8080

# 7. คำสั่งสำหรับรัน API Server เมื่อกล่องเริ่มทำงาน
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]