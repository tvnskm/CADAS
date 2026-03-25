from datetime import datetime, timezone
from pathlib import Path

from .utils import (
    build_detection_timestamp,
    is_hazard_label,
    resolve_weights_path,
    simulate_location,
)


def process_video(video_path):
    """
    Run YOLOv8 inference and return generated hazard metadata.

    The returned list contains lightweight metadata entries so Django can feed
    them into the same hazard pipeline already used by /api/report/.
    """
    try:
        import cv2
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError(
            "YOLO processing requires 'ultralytics' and 'opencv-python'."
        ) from exc

    source_path = Path(video_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    model = YOLO(str(resolve_weights_path()))
    capture = cv2.VideoCapture(str(source_path))
    if not capture.isOpened():
        raise ValueError(f"Unable to open video file: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    started_at = datetime.now(timezone.utc)
    metadata = []
    frame_index = 0
    detection_index = 0
    frame_stride = 10
    confidence_threshold = 0.55
    iou_threshold = 0.50

    try:
        while capture.isOpened():
            ok, frame = capture.read()
            if not ok:
                break

            if frame_index % frame_stride != 0:
                frame_index += 1
                continue

            results = model.predict(
                frame,
                conf=confidence_threshold,
                iou=iou_threshold,
                verbose=False,
            )
            for result in results:
                names = result.names
                label_count = len(names)

                for box in result.boxes:
                    class_id = int(box.cls[0].item())
                    confidence = float(box.conf[0].item())
                    label = names[class_id] if isinstance(names, dict) else names[class_id]

                    if not is_hazard_label(str(label), label_count):
                        continue

                    latitude, longitude = simulate_location(
                        detection_index=detection_index,
                    )
                    metadata.append(
                        {
                            "latitude": latitude,
                            "longitude": longitude,
                            "confidence": round(confidence, 3),
                            "timestamp": build_detection_timestamp(
                                started_at=started_at,
                                frame_index=frame_index,
                                fps=fps,
                            ),
                            "hazard_type": str(label).lower(),
                        }
                    )
                    detection_index += 1

            frame_index += 1
    finally:
        capture.release()

    return metadata
