from datetime import datetime, timedelta, timezone
from pathlib import Path


def resolve_weights_path() -> Path:
    project_root = Path(__file__).resolve().parent.parent
    candidate_paths = [
        project_root / "ml_model" / "weights.pt",
        Path("/Users/Mohan/runs/detect/train/weights/best.pt"),
        project_root / "Pothole_Segmentation_YOLOv8" / "yolov8n.pt",
    ]

    for candidate_path in candidate_paths:
        if candidate_path.exists():
            return candidate_path
    raise FileNotFoundError(
        "No YOLO weight file found. Add ml_model/weights.pt to enable video inference."
    )


def build_detection_timestamp(*, started_at: datetime, frame_index: int, fps: float) -> str:
    safe_fps = fps if fps and fps > 0 else 30.0
    detected_at = started_at + timedelta(seconds=frame_index / safe_fps)
    return detected_at.astimezone(timezone.utc).isoformat()


def simulate_location(*, detection_index: int) -> tuple[float, float]:
    # Video files in this project do not yet carry GPS telemetry, so we simulate
    # nearby coordinates until the real vehicle GPS stream is connected.
    base_lat = 12.971600
    base_lon = 77.594600
    offset = detection_index * 0.00002
    return round(base_lat + offset, 6), round(base_lon + offset, 6)


def is_hazard_label(label: str, known_labels_count: int) -> bool:
    normalized = label.lower().strip()
    if normalized in {"pothole", "hazard", "road_damage", "damage"}:
        return True

    # Custom pothole models are often single-class models; keep those usable.
    return known_labels_count == 1
