# Data Dictionary Draft

This file is an automatically generated draft for research-team review.
Column meanings are not confirmed. Unknown means the inspector could not infer semantics from the column name.

Source: `/Users/junnokimm/dev/synthetic-citizen-lab/data/raw/ko_KR.parquet`
Rows: 1000000
Columns: 51
Row groups: 72
SHA-256: `8128b83c300c0f9f128580f6a5f0aafadf9b87c4fb9a6fff7ad8c141be320332`

| Column | PyArrow type | DuckDB type | Null count | Null ratio | Candidate categories | Privacy risk | Semantic status |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| `uuid` | `string` | `VARCHAR` | 0 | 0.000000 | persona_id | False | unknown |
| `first_name` | `string` | `VARCHAR` | 0 | 0.000000 | sensitive_or_identifying | True | unknown |
| `middle_name` | `null` | `INTEGER` | 1000000 | 1.000000 | sensitive_or_identifying | True | unknown |
| `last_name` | `string` | `VARCHAR` | 0 | 0.000000 | sensitive_or_identifying | True | unknown |
| `sex` | `string` | `VARCHAR` | 0 | 0.000000 | demographic | False | unknown |
| `street_number` | `null` | `INTEGER` | 1000000 | 1.000000 | sensitive_or_identifying | True | unknown |
| `street_name` | `null` | `INTEGER` | 1000000 | 1.000000 | sensitive_or_identifying | True | unknown |
| `unit` | `null` | `INTEGER` | 1000000 | 1.000000 | sensitive_or_identifying | True | unknown |
| `city` | `null` | `INTEGER` | 1000000 | 1.000000 | sensitive_or_identifying | True | unknown |
| `region` | `string` | `VARCHAR` | 0 | 0.000000 | demographic | False | unknown |
| `district` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `postcode` | `null` | `INTEGER` | 1000000 | 1.000000 | sensitive_or_identifying | True | unknown |
| `country` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `age` | `int64` | `BIGINT` | 0 | 0.000000 | demographic | False | unknown |
| `marital_status` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `education_level` | `string` | `VARCHAR` | 0 | 0.000000 | socioeconomic | False | unknown |
| `bachelors_field` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `occupation` | `string` | `VARCHAR` | 0 | 0.000000 | socioeconomic | False | unknown |
| `family_type` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `housing_type` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `housing_tenure` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `military_status` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `economic_activity_status` | `string` | `VARCHAR` | 0 | 0.000000 | socioeconomic | False | unknown |
| `income_bracket` | `string` | `VARCHAR` | 0 | 0.000000 | socioeconomic | False | unknown |
| `bmi_status` | `string` | `VARCHAR` | 0 | 0.000000 | health | False | unknown |
| `blood_pressure_status` | `string` | `VARCHAR` | 0 | 0.000000 | health | False | unknown |
| `blood_sugar_status` | `string` | `VARCHAR` | 0 | 0.000000 | health | False | unknown |
| `waist_status` | `string` | `VARCHAR` | 0 | 0.000000 | health | False | unknown |
| `smoking_status` | `string` | `VARCHAR` | 0 | 0.000000 | health | False | unknown |
| `drinking_status` | `string` | `VARCHAR` | 0 | 0.000000 | health | False | unknown |
| `openness` | `string` | `VARCHAR` | 0 | 0.000000 | big_five | False | unknown |
| `conscientiousness` | `string` | `VARCHAR` | 0 | 0.000000 | big_five | False | unknown |
| `extraversion` | `string` | `VARCHAR` | 0 | 0.000000 | big_five | False | unknown |
| `agreeableness` | `string` | `VARCHAR` | 0 | 0.000000 | big_five | False | unknown |
| `neuroticism` | `string` | `VARCHAR` | 0 | 0.000000 | big_five | False | unknown |
| `cultural_background` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `skills_and_expertise` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `skills_and_expertise_list` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `career_goals_and_ambitions` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `hobbies_and_interests` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `hobbies_and_interests_list` | `string` | `VARCHAR` | 0 | 0.000000 | unknown | False | unknown |
| `professional_persona` | `string` | `VARCHAR` | 0 | 0.000000 | narrative | False | unknown |
| `finance_persona` | `string` | `VARCHAR` | 0 | 0.000000 | narrative | False | unknown |
| `healthcare_persona` | `string` | `VARCHAR` | 0 | 0.000000 | health, narrative | False | unknown |
| `sports_persona` | `string` | `VARCHAR` | 0 | 0.000000 | narrative | False | unknown |
| `arts_persona` | `string` | `VARCHAR` | 0 | 0.000000 | narrative | False | unknown |
| `travel_persona` | `string` | `VARCHAR` | 0 | 0.000000 | narrative | False | unknown |
| `culinary_persona` | `string` | `VARCHAR` | 0 | 0.000000 | narrative | False | unknown |
| `persona` | `string` | `VARCHAR` | 0 | 0.000000 | narrative | False | unknown |
| `detailed_persona` | `string` | `VARCHAR` | 0 | 0.000000 | narrative | False | unknown |
| `family_persona` | `string` | `VARCHAR` | 0 | 0.000000 | narrative | False | unknown |
