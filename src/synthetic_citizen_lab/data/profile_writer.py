"""Writers for category profile JSON, CSV, and Markdown artifacts."""

import csv
from collections.abc import Mapping

from synthetic_citizen_lab.data.profile_models import (
    AgeProfile,
    BigFiveProfile,
    CategoricalColumnProfile,
    CategoryProfileResult,
    NarrativeColumnProfile,
)


def write_profile_artifacts(result: CategoryProfileResult) -> None:
    """Write all Phase 2.5 profile artifacts."""
    _write_json(result)
    _write_csv(result)
    _write_markdown(result)


def _write_json(result: CategoryProfileResult) -> None:
    result.json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def _write_csv(result: CategoryProfileResult) -> None:
    with result.csv_path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(("section", "column", "value", "count", "ratio", "metric"))
        _write_categorical_csv(writer, result.categorical)
        _write_age_csv(writer, result.age)
        _write_big_five_csv(writer, result.big_five)
        _write_narrative_csv(writer, result.narrative)


def _write_categorical_csv(
    writer: csv.writer,
    profiles: Mapping[str, CategoricalColumnProfile],
) -> None:
    for column, profile in profiles.items():
        writer.writerow(
            ("categorical", column, "distinct_count", profile.distinct_count, "", "")
        )
        for value in profile.values:
            writer.writerow(
                (
                    "categorical",
                    column,
                    value.value,
                    value.count,
                    value.ratio,
                    "frequency",
                )
            )


def _write_age_csv(writer: csv.writer, profile: AgeProfile) -> None:
    for metric, value in (
        ("minimum", profile.minimum),
        ("maximum", profile.maximum),
        ("mean", profile.mean),
        ("median", profile.median),
    ):
        writer.writerow(("age", "age", metric, value, "", metric))
    for bucket in profile.distribution:
        writer.writerow(
            ("age", "age", bucket.value, bucket.count, bucket.ratio, "decade")
        )


def _write_big_five_csv(
    writer: csv.writer,
    profiles: Mapping[str, BigFiveProfile],
) -> None:
    for column, profile in profiles.items():
        writer.writerow(
            ("big_five", column, "distinct_count", profile.distinct_count, "", "")
        )
        writer.writerow(
            ("big_five", column, "parseable_ratio", "", profile.parseable_ratio, "")
        )
        for value in profile.examples:
            writer.writerow(("big_five", column, value, "", "", "example"))


def _write_narrative_csv(
    writer: csv.writer,
    profiles: Mapping[str, NarrativeColumnProfile],
) -> None:
    for column, profile in profiles.items():
        for metric, value in _narrative_metrics(profile):
            writer.writerow(("narrative", column, metric, value, "", metric))


def _write_markdown(result: CategoryProfileResult) -> None:
    lines = [
        "# Column Profile",
        "",
        result.caveat,
        "",
        f"Source: `{result.source_path}`",
        f"Rows: {result.row_count}",
        "",
        "## Direct UI candidates",
        "",
        ", ".join(result.direct_ui_fields) or "None",
        "",
        "## Normalization needed",
        "",
        ", ".join(result.normalization_needed) or "None",
        "",
        "## Income bracket order",
        "",
        ", ".join(str(value) for value in result.income_bracket_order) or "Unknown",
        f"Inferred: {result.income_order_inferred}",
        "",
        "## Categorical value profiles",
        "",
    ]
    for column, profile in result.categorical.items():
        lines.extend(_categorical_markdown(column, profile))
    lines.extend(_age_markdown(result.age))
    lines.extend(_big_five_markdown(result.big_five))
    lines.extend(_narrative_markdown(result.narrative))
    result.markdown_path.parent.mkdir(parents=True, exist_ok=True)
    result.markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _categorical_markdown(
    column: str,
    profile: CategoricalColumnProfile,
) -> list[str]:
    lines = [
        f"### `{column}`",
        "",
        f"Distinct count: {profile.distinct_count}",
        f"UI note: {profile.normalization_note}",
        "",
        "| Value | Count | Ratio |",
        "| --- | ---: | ---: |",
    ]
    lines.extend(
        f"| `{value.value}` | {value.count} | {value.ratio:.6f} |"
        for value in profile.values
    )
    lines.append("")
    return lines


def _age_markdown(profile: AgeProfile) -> list[str]:
    lines = [
        "## Age profile",
        "",
        f"Minimum: {profile.minimum}",
        f"Maximum: {profile.maximum}",
        f"Mean: {profile.mean:.2f}",
        f"Median: {profile.median:.2f}",
        "",
        "| Age band | Count | Ratio |",
        "| --- | ---: | ---: |",
    ]
    lines.extend(
        f"| `{bucket.value}` | {bucket.count} | {bucket.ratio:.6f} |"
        for bucket in profile.distribution
    )
    lines.append("")
    return lines


def _big_five_markdown(profiles: Mapping[str, BigFiveProfile]) -> list[str]:
    lines = ["## Big Five value format", ""]
    for column, profile in profiles.items():
        examples = ", ".join(str(value) for value in profile.examples)
        lines.append(
            f"- `{column}`: distinct={profile.distinct_count}, "
            f"numeric_parseable={profile.numeric_parseable}, "
            f"parseable_ratio={profile.parseable_ratio:.6f}, examples={examples}"
        )
    lines.append("")
    return lines


def _narrative_markdown(
    profiles: Mapping[str, NarrativeColumnProfile],
) -> list[str]:
    lines = [
        "## Narrative length and exact-duplicate profile",
        "",
        (
            "| Column | Mean length | P95 length | Max length | "
            "Duplicate row ratio | Top exact value ratio |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    lines.extend(
        f"| `{column}` | {profile.mean_length:.2f} | {profile.p95_length:.2f} | "
        f"{profile.max_length} | {profile.duplicate_row_ratio:.6f} | "
        f"{profile.top_exact_value_ratio:.6f} |"
        for column, profile in profiles.items()
    )
    lines.append("")
    return lines


def _narrative_metrics(
    profile: NarrativeColumnProfile,
) -> tuple[tuple[str, float | int], ...]:
    return (
        ("min_length", profile.min_length),
        ("mean_length", profile.mean_length),
        ("median_length", profile.median_length),
        ("p95_length", profile.p95_length),
        ("max_length", profile.max_length),
        ("distinct_count", profile.distinct_count),
        ("duplicate_row_ratio", profile.duplicate_row_ratio),
        ("top_exact_value_ratio", profile.top_exact_value_ratio),
    )
