# app/main.py
import joblib
import tensorflow as tf
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os

# --- 1. โหลดโมเดลและ Scaler ---
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
try:
    model = tf.keras.models.load_model(os.path.join(MODEL_DIR, 'model.keras'))
    scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.joblib'))
    print("✅ Model and Scaler loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model/scaler: {e}")
    model = None
    scaler = None

# --- 2. สร้างแอป FastAPI ---
# (✅ แก้บั๊กที่ 1: เรามี app = FastAPI() ที่นี่แล้ว)
app = FastAPI(title="Solar Angle Prediction API")

# --- 3. สร้าง Pydantic Model (ตัวตรวจสอบ Input) ---
class PredictionInput(BaseModel):
    day: int
    month: int
    year: int
    time_hour: int
    lux_angle_1: float
    lux_angle_2: float
    lux_angle_3: float
    lux_angle_4: float

    class Config:
        json_schema_extra = {
            "example": {
                "day": 15,
                "month": 11,
                "year": 2025,
                "time_hour": 14,
                "lux_angle_1": 850.0,
                "lux_angle_2": 1200.5,
                "lux_angle_3": 900.0,
                "lux_angle_4": 700.0
            }
        }

# --- 4. สร้าง Endpoint "/" (หน้าหลัก) ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Model API. Go to /docs to see the endpoints."}

# --- 5. สร้าง Endpoint "/predict" ---
@app.post("/predict")
async def predict(data: PredictionInput):
    if model is None or scaler is None:
        return {"error": "Model not loaded. Please check server logs."}

    try:
        # 1. แปลง Pydantic model เป็น List
        features_list = [
            data.day, data.month, data.year, data.time_hour,
            data.lux_angle_1, data.lux_angle_2, data.lux_angle_3, data.lux_angle_4
        ]

        # 2. แปลงเป็น NumPy array 2 มิติ
        features_np = np.array([features_list])

        # 3. Scale ข้อมูล
        features_scaled = scaler.transform(features_np)

        # 4. ทำนาย
        prediction_proba = model.predict(features_scaled, verbose=0)

        # 5. [ โค้ดที่แก้บั๊กแล้ว ]
        # (✅ แก้บั๊กที่ 2: เราเอา + 1 ออกแล้ว!)
        predicted_index = int(np.argmax(prediction_proba, axis=1)[0])

        # 6. ส่งคำตอบ
        return {
            "predicted_best_angle_index": predicted_index,
            "probabilities": prediction_proba[0].tolist() 
        }

    except Exception as e:
        return {"error": f"Prediction failed: {e}"}

# --- 6. (Optional) สำหรับรันทดสอบบนเครื่อง ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)