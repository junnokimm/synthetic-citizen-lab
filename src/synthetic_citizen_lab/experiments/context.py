"""Load typed persona contexts from existing sampled cohort artifacts."""

from pathlib import Path
from typing import Literal, TypedDict, assert_never, overload

import duckdb
import pyarrow.parquet as pq

from synthetic_citizen_lab.cohort.constants import BIG_FIVE_TRAITS, NARRATIVE_COLUMNS
from synthetic_citizen_lab.cohort.models import CohortDefinition
from synthetic_citizen_lab.cohort.storage import load_cohort_definition
from synthetic_citizen_lab.experiments.context_models import (
    HEALTH_SOURCE_COLUMNS,
    P1_SOURCE_COLUMNS,
    CohortArtifactNotFoundError,
    MissingPersonaColumnsError,
    MissingSampledPersonasError,
    PersonaContext,
    PersonaContextLevel,
    PersonaContextP1,
    PersonaContextP2,
    PersonaContextP3,
    PersonaId,
    PersonaNarrative,
    PersonaSourceNotFoundError,
)


class _ProjectedPersonaRow(TypedDict, total=False):
    uuid: str
    age: int
    sex: str
    region: str
    district: str
    marital_status: str
    education_level: str
    bachelors_field: str
    occupation: str
    family_type: str
    housing_type: str
    housing_tenure: str
    military_status: str
    economic_activity_status: str
    income_bracket: str
    bmi_status: str
    blood_pressure_status: str
    blood_sugar_status: str
    waist_status: str
    smoking_status: str
    drinking_status: str
    openness: str
    conscientiousness: str
    extraversion: str
    agreeableness: str
    neuroticism: str
    professional_persona: str
    finance_persona: str
    healthcare_persona: str
    sports_persona: str
    arts_persona: str
    travel_persona: str
    culinary_persona: str
    persona: str
    detailed_persona: str
    family_persona: str


@overload
def load_persona_contexts(
    cohort_dir: Path,
    level: Literal[PersonaContextLevel.P1],
) -> tuple[PersonaContextP1, ...]: ...


@overload
def load_persona_contexts(
    cohort_dir: Path,
    level: Literal[PersonaContextLevel.P2],
) -> tuple[PersonaContextP2, ...]: ...


@overload
def load_persona_contexts(
    cohort_dir: Path,
    level: Literal[PersonaContextLevel.P3],
) -> tuple[PersonaContextP3, ...]: ...


def load_persona_contexts(
    cohort_dir: Path,
    level: PersonaContextLevel,
) -> tuple[PersonaContext, ...]:
    """Return ordered P1/P2/P3 contexts for one saved cohort directory."""
    cohort_definition = _load_definition(cohort_dir)
    source_path = cohort_definition.source.path.expanduser().resolve()
    if not source_path.exists():
        raise PersonaSourceNotFoundError(source_path=source_path)
    available_columns = tuple(pq.ParquetFile(source_path).schema_arrow.names)
    projection = _projection_for_level(level, available_columns, source_path)
    rows = _load_projected_rows(source_path, cohort_definition.persona_ids, projection)
    match level:
        case PersonaContextLevel.P1:
            return tuple(_build_p1_context(row) for row in rows)
        case PersonaContextLevel.P2:
            return tuple(_build_p2_context(row) for row in rows)
        case PersonaContextLevel.P3:
            narrative_columns = tuple(
                column for column in projection if column in NARRATIVE_COLUMNS
            )
            return tuple(_build_p3_context(row, narrative_columns) for row in rows)
        case unreachable:
            assert_never(unreachable)


def _load_definition(cohort_dir: Path) -> CohortDefinition:
    cohort_path = cohort_dir / "cohort.json"
    if not cohort_path.exists():
        raise CohortArtifactNotFoundError(artifact_path=cohort_path)
    return load_cohort_definition(cohort_path)


def _projection_for_level(
    level: PersonaContextLevel,
    available_columns: tuple[str, ...],
    source_path: Path,
) -> tuple[str, ...]:
    match level:
        case PersonaContextLevel.P1:
            required_columns = P1_SOURCE_COLUMNS
            extra_columns: tuple[str, ...] = ()
        case PersonaContextLevel.P2:
            required_columns = (
                P1_SOURCE_COLUMNS + HEALTH_SOURCE_COLUMNS + BIG_FIVE_TRAITS
            )
            extra_columns = ()
        case PersonaContextLevel.P3:
            required_columns = (
                P1_SOURCE_COLUMNS + HEALTH_SOURCE_COLUMNS + BIG_FIVE_TRAITS
            )
            extra_columns = tuple(
                column for column in NARRATIVE_COLUMNS if column in available_columns
            )
        case unreachable:
            assert_never(unreachable)
    missing_columns = tuple(
        column for column in required_columns if column not in available_columns
    )
    if missing_columns:
        raise MissingPersonaColumnsError(
            source_path=source_path,
            level=level,
            columns=missing_columns,
        )
    if level == PersonaContextLevel.P3 and not extra_columns:
        raise MissingPersonaColumnsError(
            source_path=source_path,
            level=level,
            columns=NARRATIVE_COLUMNS,
        )
    return required_columns + extra_columns


def _load_projected_rows(
    source_path: Path,
    persona_ids: tuple[str, ...],
    projection: tuple[str, ...],
) -> tuple[_ProjectedPersonaRow, ...]:
    if not persona_ids:
        return ()
    placeholders = "(" + ", ".join("?" for _ in persona_ids) + ")"
    order_case = " ".join(
        f"WHEN ? THEN {index}" for index, _ in enumerate(persona_ids)
    )
    projection_sql = ", ".join(_quote_identifier(column) for column in projection)
    sql = (
        f"SELECT {projection_sql} FROM read_parquet({_sql_string(source_path)}) "
        f"WHERE {_quote_identifier('uuid')} IN {placeholders} "
        f"ORDER BY CASE {_quote_identifier('uuid')} {order_case} END"
    )
    params = (*persona_ids, *persona_ids)
    with duckdb.connect(database=":memory:") as connection:
        rows = connection.execute(sql, params).fetchall()
    row_payloads = tuple(
        dict(zip(projection, row, strict=True))
        for row in rows
    )
    loaded_ids = tuple(
        PersonaId(str(row_payload["uuid"])) for row_payload in row_payloads
    )
    expected_ids = tuple(PersonaId(persona_id) for persona_id in persona_ids)
    if loaded_ids != expected_ids:
        missing_ids = tuple(
            persona_id for persona_id in expected_ids if persona_id not in loaded_ids
        )
        raise MissingSampledPersonasError(
            source_path=source_path,
            persona_ids=missing_ids,
        )
    return row_payloads


def _build_p1_context(row: _ProjectedPersonaRow) -> PersonaContextP1:
    return PersonaContextP1.model_validate(
        {
            "persona_id": row["uuid"],
            "age": row["age"],
            "sex": row["sex"],
            "region": row["region"],
            "district": row["district"],
            "marital_status": row["marital_status"],
            "education_level": row["education_level"],
            "bachelors_field": row["bachelors_field"],
            "occupation": row["occupation"],
            "family_type": row["family_type"],
            "housing_type": row["housing_type"],
            "housing_tenure": row["housing_tenure"],
            "military_status": row["military_status"],
            "economic_activity_status": row["economic_activity_status"],
            "income_bracket": row["income_bracket"],
        }
    )


def _build_p2_context(row: _ProjectedPersonaRow) -> PersonaContextP2:
    return PersonaContextP2.model_validate(
        _build_p1_context(row).model_dump()
        | {
            "bmi_status": row["bmi_status"],
            "blood_pressure_status": row["blood_pressure_status"],
            "blood_sugar_status": row["blood_sugar_status"],
            "waist_status": row["waist_status"],
            "smoking_status": row["smoking_status"],
            "drinking_status": row["drinking_status"],
            "openness": row["openness"],
            "conscientiousness": row["conscientiousness"],
            "extraversion": row["extraversion"],
            "agreeableness": row["agreeableness"],
            "neuroticism": row["neuroticism"],
        }
    )


def _build_p3_context(
    row: _ProjectedPersonaRow,
    narrative_columns: tuple[str, ...],
) -> PersonaContextP3:
    narratives = tuple(
        PersonaNarrative(field_name=column, text=str(row[column]))
        for column in narrative_columns
        if row[column] is not None
    )
    return PersonaContextP3.model_validate(
        _build_p2_context(row).model_dump() | {"narratives": narratives}
    )


def _sql_string(path: Path) -> str:
    return "'" + str(path.expanduser().resolve()).replace("'", "''") + "'"


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'
