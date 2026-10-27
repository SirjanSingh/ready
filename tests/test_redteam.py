from pathlib import Path

import pytest
import yaml

from ready.gate import run_gate

CASES = yaml.safe_load((Path(__file__).parent.parent / "redteam" / "cases.yaml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_redteam(case, shop):
    v = run_gate(case["issue"].strip(), shop, use_model=False)
    if "expect" in case:
        assert v.status == case["expect"], (v.question, v.findings)
    if "expect_footprint_excludes" in case:
        assert case["expect_footprint_excludes"] not in v.footprint
