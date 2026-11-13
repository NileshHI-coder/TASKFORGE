import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.routes.data_analysis import build_analysis


def test_build_analysis_reports_quality_and_numeric_statistics():
    frame = pd.DataFrame({
        "market": ["Anand", "Vadodara", "Anand"],
        "price": [100.0, 120.0, None],
        "quantity": [2, 3, 2],
    })
    result = build_analysis(frame)
    assert result["shape"] == {"rows": 3, "columns": 3}
    assert result["total_missing"] == 1
    assert result["numeric_summary"]["price"]["mean"] == 110.0
    assert result["correlations"][0]["x"] == "price"
    assert "price" in result["histograms"]
    assert result["preview"]["rows"][2][1] is None


def test_build_analysis_handles_no_numeric_columns():
    result = build_analysis(pd.DataFrame({"crop": ["cotton", "wheat"]}))
    assert result["numeric_summary"] == {}
    assert result["correlations"] == []
    assert result["categorical_distributions"]["crop"][0]["value"] == 1
