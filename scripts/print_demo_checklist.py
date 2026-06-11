from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import get_runtime_info, settings


def main() -> None:
    demo_video = PROJECT_ROOT / "sample_videos" / "demo.mp4"
    attribution_file = PROJECT_ROOT / "sample_videos" / "ATTRIBUTION.md"
    yolo_model = settings.yolo_model_path
    runtime = get_runtime_info()

    validation_benchmarks = settings.benchmark_output_dir
    validation_frames = settings.video_output_dir / "validation_frames"

    print("====================================================")
    print("          SMARTKUET DEMO CHECKLIST & STATUS         ")
    print("====================================================")

    print(f"1. sample_videos/demo.mp4 exists: {demo_video.exists()}")
    print(f"2. sample_videos/ATTRIBUTION.md exists: {attribution_file.exists()}")
    print(f"3. models/yolov8n.pt exists:       {yolo_model.exists()}")
    print(
        f"4. PyTorch CUDA status:            "
        f"{'Available' if runtime.get('cuda_available') else 'Unavailable (CPU fallback)'}"
    )
    print(
        f"5. Runs benchmarks directory:      "
        f"{validation_benchmarks.exists()} ({validation_benchmarks})"
    )
    print(
        f"6. Validation frames directory:    "
        f"{validation_frames.exists()} ({validation_frames})"
    )
    print()
    print("SAFETY REMINDERS:")
    print("----------------------------------------------------")
    print("WARNING: Do NOT add or commit demo.mp4 to Git.")
    print("Make sure .gitignore is configured correctly.")
    print()
    print("Exact commands to run:")
    print("----------------------------------------------------")
    print("pytest")
    print("python scripts/check_runtime.py")
    print(
        "python scripts/validate_demo_video.py --source sample_videos/demo.mp4 --seconds 30 --write-summary"
    )
    print("uvicorn api.main:app --reload --port 8002")
    print("====================================================")


if __name__ == "__main__":
    main()
