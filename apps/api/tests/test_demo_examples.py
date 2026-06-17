import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DEMO_DIR = REPO_ROOT / "examples" / "demo-thesis"


def test_demo_thesis_project_metadata_has_workflow_fields() -> None:
    project = json.loads((DEMO_DIR / "project.json").read_text(encoding="utf-8"))

    required_fields = {
        "title",
        "problem_statement",
        "research_gap",
        "methodology_summary",
        "results_summary",
    }

    missing_fields = [field for field in required_fields if not project.get(field)]
    assert missing_fields == []


def test_demo_thesis_files_include_review_material() -> None:
    thesis_text = (DEMO_DIR / "thesis_draft.txt").read_text(encoding="utf-8")
    references = (DEMO_DIR / "references.bib").read_text(encoding="utf-8")

    for heading in ("Problem Statement", "Research Gap", "Methodology", "Results Summary"):
        assert heading in thesis_text

    assert "@inproceedings" in references
    assert "@article" in references


def test_demo_results_csv_has_model_rows() -> None:
    with (DEMO_DIR / "results.csv").open(encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert {row["model"] for row in rows} == {
        "persistence",
        "gradient_boosting",
        "lstm",
        "temporal_fusion_transformer",
    }
    assert all(row["mae_kwh"] for row in rows)
