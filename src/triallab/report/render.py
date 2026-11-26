"""`triallab report`: a plain, self-contained HTML summary built from the evidence bundle.

This is the unbranded local view. The published research report is produced by
Smart Mobile House's separate report system from the same evidence bundle.
Statuses such as "not run" or "withheld" are shown as text, never as numbers.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from triallab.report.export import export_report_data

TEMPLATES = Path(__file__).parent / "templates"


def pct(value: Any) -> str:
    return "—" if value is None else f"{float(value) * 100:.1f}%"


def num(value: Any, digits: int = 1) -> str:
    return "—" if value is None else f"{float(value):,.{digits}f}"


def build_report(run_ids: list[str], out_file: Path, outputs: Path | None = None) -> Path:
    with tempfile.TemporaryDirectory() as tmp:
        bundle = json.loads(export_report_data(run_ids, Path(tmp) / "bundle.json", outputs).read_text())
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html", "j2"]))
    env.filters.update(pct=pct, num=num)
    html = env.get_template("report.html.j2").render(bundle=bundle)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html)
    return out_file
