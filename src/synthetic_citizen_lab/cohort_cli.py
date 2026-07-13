"""Command line entry point for cohort counting and seeded sampling."""

import json
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from synthetic_citizen_lab.cohort.constants import FILTER_FIELD_TO_COLUMN
from synthetic_citizen_lab.cohort.options import CohortOptions
from synthetic_citizen_lab.cohort.sampler import CohortSampler
from synthetic_citizen_lab.cohort_cli_args import (
    DEFAULT_SOURCE_PATH,
    CohortCliUsageError,
    next_value,
    parse_common,
    request_from_args,
    request_from_config,
)


def main(args: Sequence[str] | None = None) -> int:
    """Run the cohort CLI."""
    argv = tuple(sys.argv[1:] if args is None else args)
    if not argv or argv[0] in {"-h", "--help"}:
        _print_help()
        return 0
    command = argv[0]
    command_args = argv[1:]
    try:
        match command:
            case "options":
                _run_options(command_args)
            case "districts":
                _run_districts(command_args)
            case "occupations":
                _run_occupations(command_args)
            case "count":
                _run_count(command_args)
            case "sample":
                _run_sample(command_args)
            case _:
                _raise_usage(f"Unsupported command: {command}")
    except (CohortCliUsageError, ValidationError, ValueError) as error:
        sys.stderr.write(f"error: {error}\n")
        return 2
    return 0


def _run_options(argv: Sequence[str]) -> None:
    source_path = DEFAULT_SOURCE_PATH
    column = "region"
    with_counts = False
    index = 0
    while index < len(argv):
        current_arg = argv[index]
        match current_arg:
            case "--source":
                source_path = Path(next_value(argv, index, current_arg))
                index += 2
            case "--column":
                column = next_value(argv, index, current_arg)
                index += 2
            case "--with-counts":
                with_counts = True
                index += 1
            case _ if current_arg.startswith("--"):
                message = f"Unsupported option for options: {current_arg}"
                _raise_usage(message)
            case _:
                source_path = Path(current_arg)
                index += 1
    if column not in set(FILTER_FIELD_TO_COLUMN.values()):
        message = f"Unsupported option column: {column}"
        _raise_usage(message)
    _print_lines(CohortOptions(source_path).distinct_values(column, with_counts))


def _run_districts(argv: Sequence[str]) -> None:
    source_path = DEFAULT_SOURCE_PATH
    regions: list[str] = []
    index = 0
    while index < len(argv):
        current_arg = argv[index]
        match current_arg:
            case "--source":
                source_path = Path(next_value(argv, index, current_arg))
                index += 2
            case "--region":
                regions.append(next_value(argv, index, current_arg))
                index += 2
            case _ if current_arg.startswith("--"):
                message = f"Unsupported option for districts: {current_arg}"
                _raise_usage(message)
            case _:
                source_path = Path(current_arg)
                index += 1
    _print_lines(CohortOptions(source_path).districts(tuple(regions)))


def _run_occupations(argv: Sequence[str]) -> None:
    source_path = DEFAULT_SOURCE_PATH
    search = ""
    index = 0
    while index < len(argv):
        current_arg = argv[index]
        match current_arg:
            case "--source":
                source_path = Path(next_value(argv, index, current_arg))
                index += 2
            case "--search":
                search = next_value(argv, index, current_arg)
                index += 2
            case _ if current_arg.startswith("--"):
                message = f"Unsupported option for occupations: {current_arg}"
                _raise_usage(message)
            case _:
                source_path = Path(current_arg)
                index += 1
    _print_lines(CohortOptions(source_path).occupation_search(search))


def _run_count(argv: Sequence[str]) -> None:
    parsed = parse_common(argv, require_sampling=False)
    filters = (
        request_from_config(parsed).filters if parsed.config_path else parsed.filters
    )
    matching_count = CohortSampler(parsed.source_path).matching_count(filters)
    sys.stdout.write(f"matching_count={matching_count}\n")


def _run_sample(argv: Sequence[str]) -> None:
    parsed = parse_common(argv, require_sampling=True)
    request = (
        request_from_config(parsed) if parsed.config_path else request_from_args(parsed)
    )
    cohort_dir = CohortSampler(parsed.source_path).save_sample(
        request,
        output_dir=parsed.output_dir,
    )
    sys.stdout.write(f"cohort_dir={cohort_dir}\n")


def _print_lines(values: tuple[str, ...]) -> None:
    sys.stdout.write("\n".join(values) + ("\n" if values else ""))


def _print_help() -> None:
    commands = {
        "options": "List values for a filter column.",
        "districts": "List districts, optionally for repeated --region values.",
        "occupations": "Search occupation labels with --search.",
        "count": "Count personas matching filter options or --config.",
        "sample": "Save deterministic sample artifacts from options or --config.",
    }
    sys.stdout.write(json.dumps(commands, ensure_ascii=False, indent=2) + "\n")


def _raise_usage(message: str) -> None:
    raise CohortCliUsageError(message)
