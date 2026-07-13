"""Storage helpers for sampled cohort artifacts."""

from csv import writer
from pathlib import Path

from synthetic_citizen_lab.cohort.models import CohortDefinition


def write_cohort_definition(path: Path, definition: CohortDefinition) -> None:
    """Write cohort metadata JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(definition.model_dump_json(indent=2), encoding="utf-8")


def load_cohort_definition(path: Path) -> CohortDefinition:
    """Load cohort metadata JSON."""
    return CohortDefinition.model_validate_json(path.read_text(encoding="utf-8"))


def write_sample_ids(path: Path, persona_ids: tuple[str, ...]) -> None:
    """Write one uuid column for sampled personas."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        csv_writer = writer(target)
        csv_writer.writerow(("uuid",))
        for persona_id in persona_ids:
            csv_writer.writerow((persona_id,))


def write_preview(
    path: Path, rows: tuple[dict[str, str | int | float | bool | None], ...]
) -> None:
    """Write a safe sample preview CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns = tuple(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as target:
        csv_writer = writer(target)
        csv_writer.writerow(columns)
        for row in rows:
            csv_writer.writerow(tuple(row[column] for column in columns))
