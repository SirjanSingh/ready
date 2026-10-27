import shutil
import subprocess
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "shop"


@pytest.fixture
def shop(tmp_path: Path) -> Path:
    dst = tmp_path / "shop"
    shutil.copytree(FIXTURE, dst)
    subprocess.run(["git", "init", "-q"], cwd=dst, check=True)
    subprocess.run(["git", "add", "-A"], cwd=dst, check=True)
    return dst


@pytest.fixture(autouse=True)
def no_model(monkeypatch):
    # Tests never call a real provider.
    monkeypatch.delenv("READY_API_KEY", raising=False)


DEMO = Path(__file__).parent / "fixtures" / "demo"


@pytest.fixture
def demo(tmp_path: Path) -> Path:
    # A copy of SirjanSingh/ready-demo's code, so the demo's verdicts are pinned by tests.
    dst = tmp_path / "demo"
    shutil.copytree(DEMO, dst)
    subprocess.run(["git", "init", "-q"], cwd=dst, check=True)
    subprocess.run(["git", "add", "-A"], cwd=dst, check=True)
    return dst
