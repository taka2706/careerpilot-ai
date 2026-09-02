"""Run all offline evaluation scenarios and save a JSON report."""

from pathlib import Path

from app.db.init_db import initialize_database
from app.db.session import SessionLocal
from app.evaluation.runner import EvaluationRunner


def main() -> None:
    initialize_database()
    with SessionLocal() as session:
        report = EvaluationRunner(session).run_all()
    output_path = Path("data/evaluation-report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    print(f"Evaluation report written to {output_path} ({report.total_scenarios} scenarios).")


if __name__ == "__main__":
    main()
