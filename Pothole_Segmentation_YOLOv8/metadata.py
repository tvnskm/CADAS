from ultralytics import YOLO
import cv2
import json
from datetime import datetime

# Load trained model
model = YOLO("/Users/Mohan/runs/detect/train/weights/best.pt")

# Open video
cap = cv2.VideoCapture("sample_video.mp4")

vehicle_id = "V001"

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls)
            confidence = float(box.conf)

            metadata = {
                "vehicle_id": vehicle_id,
                "object_type": result.names[class_id],
                "confidence": round(confidence, 3),
                "latitude": 12.8234,   # simulated GPS
                "longitude": 80.0445,
                "timestamp": datetime.now().isoformat()
            }

            print(json.dumps(metadata, indent=4))

    # Optional: show live detection window
    annotated_frame = results[0].plot()
    cv2.imshow("Stage 1 - Edge Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()