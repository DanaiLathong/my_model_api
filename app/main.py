@app.post("/predict")
async def predict(data: PredictionInput):
    if model is None or scaler is None:
        return {"error": "Model not loaded. Please check server logs."}

    try:
        # 1. แปลง Pydantic model เป็น List (ตามลำดับที่ใช้เทรน)
        features_list = [
            data.day, data.month, data.year, data.time_hour,
            data.lux_angle_1, data.lux_angle_2, data.lux_angle_3, data.lux_angle_4
        ]

        # 2. แปลงเป็น NumPy array 2 มิติ
        features_np = np.array([features_list])

        # 3. Scale ข้อมูล
        features_scaled = scaler.transform(features_np)

        # 4. ทำนาย (นี่คือผลลัพธ์จาก AI)
        prediction_proba = model.predict(features_scaled, verbose=0)

        # 5. [โค้ดที่ถูกต้องอยู่ตรงนี้!] 
        #    หา Index ที่มี "ความน่าจะเป็น" (prediction_proba) สูงสุด
        predicted_index = int(np.argmax(prediction_proba, axis=1)[0])

        # 6. ส่งคำตอบ
        return {
            "predicted_best_angle_index": predicted_index,
            "probabilities": prediction_proba[0].tolist() 
        }

    except Exception as e:
        return {"error": f"Prediction failed: {e}"}