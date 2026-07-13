"""Phase 2.5 column targets for synthetic-persona profiling."""

from typing import Final

DEMOGRAPHIC_COLUMNS: Final[tuple[str, ...]] = (
    "sex",
    "region",
    "district",
    "marital_status",
)
SOCIOECONOMIC_COLUMNS: Final[tuple[str, ...]] = (
    "education_level",
    "bachelors_field",
    "occupation",
    "family_type",
    "housing_type",
    "housing_tenure",
    "military_status",
    "economic_activity_status",
    "income_bracket",
)
HEALTH_COLUMNS: Final[tuple[str, ...]] = (
    "bmi_status",
    "blood_pressure_status",
    "blood_sugar_status",
    "waist_status",
    "smoking_status",
    "drinking_status",
)
BIG_FIVE_COLUMNS: Final[tuple[str, ...]] = (
    "openness",
    "conscientiousness",
    "extraversion",
    "agreeableness",
    "neuroticism",
)
NARRATIVE_COLUMNS: Final[tuple[str, ...]] = (
    "professional_persona",
    "finance_persona",
    "healthcare_persona",
    "sports_persona",
    "arts_persona",
    "travel_persona",
    "culinary_persona",
    "persona",
    "detailed_persona",
    "family_persona",
)
CATEGORICAL_COLUMNS: Final[tuple[str, ...]] = (
    *DEMOGRAPHIC_COLUMNS,
    *SOCIOECONOMIC_COLUMNS,
    *HEALTH_COLUMNS,
)
DIRECT_UI_DISTINCT_LIMIT: Final[int] = 100
PROFILE_CAVEAT: Final[str] = (
    "These profiles describe distributions inside a synthetic dataset only; "
    "they are not Korean population statistics."
)
