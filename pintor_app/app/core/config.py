from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppConfig:
    project_root: Path
    data_dir: Path
    db_path: Path
    timezone: str = "America/Sao_Paulo"


def load_config() -> AppConfig:
    # app/ -> project root
    project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "data"
    db_path = data_dir / "app.db"
    return AppConfig(project_root=project_root, data_dir=data_dir, db_path=db_path)
