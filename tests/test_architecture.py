from pathlib import Path


def test_directories_exist():
    project_root = Path(__file__).resolve().parent.parent
    backend_dir = project_root / "backend"
    frontend_dir = project_root / "frontend"
    assert backend_dir.is_dir(), f"Expected {backend_dir} to exist"
    assert frontend_dir.is_dir(), f"Expected {frontend_dir} to exist"