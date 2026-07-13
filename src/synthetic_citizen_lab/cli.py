"""Command line entry points for synthetic-citizen-lab."""

import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from synthetic_citizen_lab.data.inspector import (
    DEFAULT_SAMPLE_LIMIT,
    inspect_parquet,
    write_dictionary,
)

DEFAULT_SOURCE_PATH: Final[Path] = Path("data/raw/ko_KR.parquet")
DEFAULT_OUTPUT_DIR: Final[Path] = Path("outputs/data_inspection")
DEFAULT_DOCS_DICTIONARY: Final[Path] = Path("docs/data_dictionary.md")


@dataclass(frozen=True, slots=True)
class InspectDataArgs:
    """Parsed CLI arguments for the data inspection command."""

    source_path: Path
    output_dir: Path
    sample_limit: int


class CliUsageError(Exception):
    """Raised when CLI arguments do not match the supported command shape."""


def main(args: Sequence[str] | None = None) -> int:
    """Run the data inspection CLI."""
    parsed_args = _parse_args(tuple(sys.argv[1:]) if args is None else args)
    result = inspect_parquet(
        parsed_args.source_path,
        output_dir=parsed_args.output_dir,
        sample_limit=parsed_args.sample_limit,
    )
    write_dictionary(DEFAULT_DOCS_DICTIONARY, result)
    _print_summary(result.json_path, DEFAULT_DOCS_DICTIONARY)
    return 0


def _parse_args(argv: Sequence[str]) -> InspectDataArgs:
    source_path = DEFAULT_SOURCE_PATH
    output_dir = DEFAULT_OUTPUT_DIR
    sample_limit = DEFAULT_SAMPLE_LIMIT
    index = 0
    while index < len(argv):
        current_arg = argv[index]
        if current_arg == "--output-dir":
            output_dir = Path(_next_value(argv, index, current_arg))
            index += 2
        elif current_arg == "--sample-limit":
            sample_limit = int(_next_value(argv, index, current_arg))
            index += 2
        elif current_arg.startswith("--"):
            message = f"Unsupported option: {current_arg}"
            raise CliUsageError(message)
        else:
            source_path = Path(current_arg)
            index += 1
    return InspectDataArgs(
        source_path=source_path,
        output_dir=output_dir,
        sample_limit=sample_limit,
    )


def _next_value(argv: Sequence[str], index: int, option: str) -> str:
    value_index = index + 1
    if value_index >= len(argv):
        message = f"Missing value for {option}"
        raise CliUsageError(message)
    return argv[value_index]


def _print_summary(json_path: Path, dictionary_path: Path) -> None:
    lines = (
        f"inspection_json={json_path}",
        f"data_dictionary={dictionary_path}",
    )
    sys.stdout.write("\n".join(lines) + "\n")
