"""Synthetic citizen policy-response pretest research package."""

from typing import Final

__version__: Final[str] = "0.1.0"

PROJECT_NAME: Final[str] = "합성 시민 Agent 기반 정책 반응 가상 실험 환경"
NON_CLAIM: Final[str] = (
    "This package supports exploratory synthetic-persona pretests only; it does "
    "not predict real public opinion or policy acceptance rates."
)

__all__: Final[tuple[str, ...]] = ("NON_CLAIM", "PROJECT_NAME", "__version__")
