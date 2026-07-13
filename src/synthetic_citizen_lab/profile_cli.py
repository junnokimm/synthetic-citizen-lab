"""Command line entry point for category profiling."""

import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from synthetic_citizen_lab.data.profiler import DEFAULT_TOP_N, profile_parquet

DEFAULT_SOURCE_PATH: Final[Path] = Path("data/raw/ko_KR.parquet")
DEFAULT_OUTPUT_DIR: Final[Path] = Path("outputs/data_inspection")


@dataclass(frozen=True, slots=True)
class ProfileArgs:
    """Parsed CLI arguments for category profiling."""

    source_path: Path
    output_dir: Path
    top_n: int


class ProfileCliUsageError(Exception):
    """Raised when profile CLI arguments are unsupported."""


def main(args: Sequence[str] | None = None) -> int:
    """Run category profiling for configured Phase 2.5 columns."""
    parsed_args = _parse_args(tuple(sys.argv[1:]) if args is None else args)
    result = profile_parquet(
        parsed_args.source_path,
        output_dir=parsed_args.output_dir,
        top_n=parsed_args.top_n,
    )
    _print_summary(result.json_path, result.csv_path, result.markdown_path)
    return 0


def _parse_args(argv: Sequence[str]) -> ProfileArgs:
    source_path = DEFAULT_SOURCE_PATH
    output_dir = DEFAULT_OUTPUT_DIR
    top_n = DEFAULT_TOP_N
    index = 0
    while index < len(argv):
        current_arg = argv[index]
        if current_arg == "--output-dir":
            output_dir = Path(_next_value(argv, index, current_arg))
            index += 2
        elif current_arg == "--top-n":
            top_n = int(_next_value(argv, index, current_arg))
            index += 2
        elif current_arg.startswith("--"):
            message = f"Unsupported option: {current_arg}"
            raise ProfileCliUsageError(message)
        else:
            source_path = Path(current_arg)
            index += 1
    return ProfileArgs(source_path=source_path, output_dir=output_dir, top_n=top_n)


def _next_value(argv: Sequence[str], index: int, option: str) -> str:
    value_index = index + 1
    if value_index >= len(argv):
        message = f"Missing value for {option}"
        raise ProfileCliUsageError(message)
    return argv[value_index]


def _print_summary(json_path: Path, csv_path: Path, markdown_path: Path) -> None:
    lines = (
        f"category_profiles_json={json_path}",
        f"category_profiles_csv={csv_path}",
        f"column_profile_markdown={markdown_path}",
    )
    sys.stdout.write("\n".join(lines) + "\n")
