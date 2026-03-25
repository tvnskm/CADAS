from flask import Flask, render_template, request
from ultralytics import YOLO
import os
import json
from datetime import datetime

app = Flask(__name__)

# Load trained model
model = YOLO("/Users/Mohan/runs/detect/train/weights/best.pt")

UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    metadata_output = []
    output_video = None

    if request.method == "POST":
        file = request.files["video"]
        if file:
            video_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(video_path)

            # Run detection
            results = model(video_path, save=True)

            for result in results:
                for box in result.boxes:
                    metadata = {
                        "vehicle_id": "V001",
                        "object_type": result.names[int(box.cls)],
                        "confidence": round(float(box.conf), 3),
                        "latitude": 12.8234,
                        "longitude": 80.0445,
                        "timestamp": datetime.now().isoformat()
                    }
                    metadata_output.append(metadata)

            output_video = "runs/detect/predict/" + file.filename

    return render_template("index.html",
                           metadata=json.dumps(metadata_output, indent=4),
                       output_video=output_video)

if __name__ == "__main__":
    print("Starting Flask Server...")
    app.run(host="0.0.0.0", port=5050, debug=True)