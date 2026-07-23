# Column Profile

These profiles describe distributions inside a synthetic dataset only; they are not Korean population statistics.

Source: `/private/var/folders/vx/cb6syl497_v7jfjxl6rxdrc40000gn/T/pytest-of-junnokimm/pytest-43/test_profile_parquet_summarize0/fixture.parquet`
Rows: 4

## Direct UI candidates

sex, region, district, education_level, economic_activity_status, income_bracket, bmi_status

## Normalization needed

None

## Income bracket order

Unknown
Inferred: True

## Categorical value profiles

### `sex`

Distinct count: 2
UI note: Suitable for direct filter UI after research-team label review.

| Value | Count | Ratio |
| --- | ---: | ---: |
| `female` | 3 | 0.750000 |
| `male` | 1 | 0.250000 |

### `region`

Distinct count: 3
UI note: Suitable for direct filter UI after research-team label review.

| Value | Count | Ratio |
| --- | ---: | ---: |
| `Seoul` | 2 | 0.500000 |
| `Busan` | 1 | 0.250000 |

### `district`

Distinct count: 3
UI note: Suitable for direct filter UI after research-team label review.

| Value | Count | Ratio |
| --- | ---: | ---: |
| `A` | 2 | 0.500000 |
| `B` | 1 | 0.250000 |

### `education_level`

Distinct count: 3
UI note: Suitable for direct filter UI after research-team label review.

| Value | Count | Ratio |
| --- | ---: | ---: |
| `college` | 2 | 0.500000 |
| `grad` | 1 | 0.250000 |

### `economic_activity_status`

Distinct count: 2
UI note: Suitable for direct filter UI after research-team label review.

| Value | Count | Ratio |
| --- | ---: | ---: |
| `active` | 3 | 0.750000 |
| `inactive` | 1 | 0.250000 |

### `income_bracket`

Distinct count: 3
UI note: Review value order before using as an ordered cohort filter.

| Value | Count | Ratio |
| --- | ---: | ---: |
| `middle` | 2 | 0.500000 |
| `high` | 1 | 0.250000 |

### `bmi_status`

Distinct count: 3
UI note: Suitable for direct filter UI after research-team label review.

| Value | Count | Ratio |
| --- | ---: | ---: |
| `normal` | 2 | 0.500000 |
| `high` | 1 | 0.250000 |

## Age profile

Minimum: 19
Maximum: 67
Mean: 40.25
Median: 37.50

| Age band | Count | Ratio |
| --- | ---: | ---: |
| `10s` | 1 | 0.250000 |
| `30s` | 1 | 0.250000 |
| `40s` | 1 | 0.250000 |
| `60s` | 1 | 0.250000 |

## Big Five value format

- `openness`: distinct=3, numeric_parseable=False, parseable_ratio=0.000000, examples=high, low, medium

## Narrative length and exact-duplicate profile

| Column | Mean length | P95 length | Max length | Duplicate row ratio | Top exact value ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| `persona` | 9.75 | 14.95 | 16 | 0.250000 | 0.500000 |

