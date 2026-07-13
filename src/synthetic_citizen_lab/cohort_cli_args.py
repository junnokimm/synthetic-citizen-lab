"""Argument parsing helpers for the cohort CLI."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from synthetic_citizen_lab.cohort.models import (
    CohortFilter,
    CohortRequest,
    SamplingSpec,
)

DEFAULT_SOURCE_PATH: Final[Path] = Path("data/raw/ko_KR.parquet")
DEFAULT_OUTPUT_DIR: Final[Path] = Path("outputs/cohorts")
OPTION_TO_FILTER_FIELD: Final[dict[str, str]] = {
    "--sex": "sexes",
    "--region": "regions",
    "--district": "districts",
    "--marital-status": "marital_statuses",
    "--education-level": "education_levels",
    "--bachelors-field": "bachelors_fields",
    "--occupation": "occupations",
    "--family-type": "family_types",
    "--housing-type": "housing_types",
    "--housing-tenure": "housing_tenures",
    "--military-status": "military_statuses",
    "--economic-activity-status": "economic_activity_statuses",
    "--income-bracket": "income_brackets",
    "--bmi-status": "bmi_statuses",
    "--blood-pressure-status": "blood_pressure_statuses",
    "--blood-sugar-status": "blood_sugar_statuses",
    "--waist-status": "waist_statuses",
    "--smoking-status": "smoking_statuses",
    "--drinking-status": "drinking_statuses",
}


@dataclass(frozen=True, slots=True)
class CohortCliUsageError(Exception):
    """Raised when cohort CLI arguments are unsupported."""

    message: str

    def __str__(self) -> str:
        """Return the user-facing CLI error message."""
        return self.message


@dataclass(frozen=True, slots=True)
class CommonArgs:
    """Shared parsed arguments for cohort CLI subcommands."""

    source_path: Path
    output_dir: Path
    config_path: Path | None
    name: str
    filters: CohortFilter
    sampling: SamplingSpec | None


def parse_common(argv: Sequence[str], *, require_sampling: bool) -> CommonArgs:
    """Parse shared count/sample options."""
    state = _CommonParseState()
    index = 0
    while index < len(argv):
        current_arg = argv[index]
        index = _parse_common_token(state, argv, index, current_arg)
    return state.to_args(require_sampling=require_sampling)


def request_from_config(parsed: CommonArgs) -> CohortRequest:
    """Load a cohort request from parsed --config arguments."""
    if parsed.config_path is None:
        message = "Missing config path."
        raise CohortCliUsageError(message)
    return CohortRequest.model_validate_json(
        parsed.config_path.read_text(encoding="utf-8")
    )


def request_from_args(parsed: CommonArgs) -> CohortRequest:
    """Build a cohort request from parsed inline CLI arguments."""
    if parsed.sampling is None:
        message = "Missing sampling specification."
        raise CohortCliUsageError(message)
    return CohortRequest(
        name=parsed.name, filters=parsed.filters, sampling=parsed.sampling
    )


@dataclass(slots=True)
class _CommonParseState:
    source_path: Path = DEFAULT_SOURCE_PATH
    output_dir: Path = DEFAULT_OUTPUT_DIR
    config_path: Path | None = None
    name: str = "cohort"
    age_min: int | None = None
    age_max: int | None = None
    occupation_search: str | None = None
    sample_size: int | None = None
    seed: int | None = None
    field_values: dict[str, list[str]] | None = None

    def add_filter_value(self, option: str, value: str) -> None:
        field_name = OPTION_TO_FILTER_FIELD[option]
        values = {} if self.field_values is None else self.field_values
        values.setdefault(field_name, []).append(value)
        self.field_values = values

    def to_args(self, *, require_sampling: bool) -> CommonArgs:
        sampling = _sampling_spec(
            self.sample_size,
            self.seed,
            require_sampling and self.config_path is None,
        )
        return CommonArgs(
            source_path=self.source_path,
            output_dir=self.output_dir,
            config_path=self.config_path,
            name=self.name,
            filters=CohortFilter(
                age_min=self.age_min,
                age_max=self.age_max,
                occupation_search=self.occupation_search,
                **_filter_values(self.field_values),
            ),
            sampling=sampling,
        )


def _parse_common_token(
    state: _CommonParseState,
    argv: Sequence[str],
    index: int,
    current_arg: str,
) -> int:
    if _parse_path_token(state, argv, index, current_arg):
        return index + 2
    if _parse_scalar_token(state, argv, index, current_arg):
        return index + 2
    if current_arg in OPTION_TO_FILTER_FIELD:
        state.add_filter_value(current_arg, next_value(argv, index, current_arg))
        return index + 2
    if current_arg.startswith("--"):
        message = f"Unsupported option: {current_arg}"
        raise CohortCliUsageError(message)
    state.source_path = Path(current_arg)
    return index + 1


def _parse_path_token(
    state: _CommonParseState,
    argv: Sequence[str],
    index: int,
    current_arg: str,
) -> bool:
    match current_arg:
        case "--source":
            state.source_path = Path(next_value(argv, index, current_arg))
        case "--output-dir":
            state.output_dir = Path(next_value(argv, index, current_arg))
        case "--config":
            state.config_path = Path(next_value(argv, index, current_arg))
        case _:
            return False
    return True


def _parse_scalar_token(
    state: _CommonParseState,
    argv: Sequence[str],
    index: int,
    current_arg: str,
) -> bool:
    match current_arg:
        case "--name":
            state.name = next_value(argv, index, current_arg)
        case "--age-min":
            state.age_min = int(next_value(argv, index, current_arg))
        case "--age-max":
            state.age_max = int(next_value(argv, index, current_arg))
        case "--occupation-search":
            state.occupation_search = next_value(argv, index, current_arg)
        case "--sample-size":
            state.sample_size = int(next_value(argv, index, current_arg))
        case "--seed":
            state.seed = int(next_value(argv, index, current_arg))
        case _:
            return False
    return True


def _sampling_spec(
    sample_size: int | None, seed: int | None, require_sampling: bool
) -> SamplingSpec | None:
    if not require_sampling:
        return None
    if sample_size is None or seed is None:
        message = (
            "sample requires --sample-size and --seed unless --config is supplied."
        )
        raise CohortCliUsageError(message)
    return SamplingSpec(sample_size=sample_size, seed=seed)


def _filter_values(values: dict[str, list[str]] | None) -> dict[str, tuple[str, ...]]:
    if values is None:
        return {}
    return {key: tuple(value) for key, value in values.items()}


def next_value(argv: Sequence[str], index: int, option: str) -> str:
    """Return the required value following a CLI option."""
    value_index = index + 1
    if value_index >= len(argv):
        message = f"Missing value for {option}"
        raise CohortCliUsageError(message)
    return argv[value_index]
