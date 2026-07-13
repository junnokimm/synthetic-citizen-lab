from synthetic_citizen_lab import NON_CLAIM, PROJECT_NAME, __version__


def test_package_import_exposes_project_metadata() -> None:
    # Given: Phase 1 only needs an importable package with research guardrails.
    # When: importing the top-level package metadata.
    # Then: the package exposes the project identity and non-claim text.
    assert __version__ == "0.1.0"
    assert "합성 시민" in PROJECT_NAME
    assert "does not predict real public opinion" in NON_CLAIM
