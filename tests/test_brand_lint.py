"""Brand lint: no Planet City exhibition asset paths; synthetic-only markers."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_SUBSTRINGS = [
    "planet-city-exhibition",
    "Views of Planet City",
    "/Are.na/",
    "zillow.com",
    "yelp.com",
    "twitter.com",
]


def _iter_text_files():
    skip_dirs = {".venv", "__pycache__", ".git", "*.egg-info"}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part.startswith(".venv") or part == "__pycache__" for part in path.parts):
            continue
        if path.suffix.lower() not in {".py", ".md", ".json", ".toml", ".txt", ".yaml", ".yml", ".cff"}:
            continue
        # Docs may mention Planet City as lineage prose — allow PROVENANCE/ATTRIBUTION/CITATION/README
        # only for attribution words, but forbid exhibition asset *paths*.
        yield path


def test_no_exhibition_asset_paths_in_code_and_fixtures():
    offenders = []
    for path in _iter_text_files():
        # Attribution docs may name the research project; scan code+fixtures only for paths.
        if path.parts[-2:] and path.name in {
            "PROVENANCE.md",
            "ATTRIBUTION.md",
            "CITATION.cff",
            "README.md",
            "LIMITATIONS.md",
            "TEMPLATE.md",
        }:
            # Still forbid concrete CDN / Are.na asset URLs in docs.
            text = path.read_text(encoding="utf-8", errors="ignore")
            for bad in ("squarespace-cdn.com", "imgix.net", "dropbox.com/s/"):
                if bad in text.lower():
                    offenders.append(f"{path.relative_to(ROOT)}: {bad}")
            continue
        if "src" not in path.parts and "fixtures" not in path.parts and "tests" not in path.parts:
            if path.suffix != ".py":
                continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for bad in FORBIDDEN_SUBSTRINGS:
            if bad in text:
                # Allow test file itself to mention forbidden strings as literals under test.
                if path.name == "test_brand_lint.py":
                    continue
                offenders.append(f"{path.relative_to(ROOT)}: {bad}")
    assert not offenders, "brand lint failed:\n" + "\n".join(offenders)


def test_readme_declares_synthetic_and_not_sciarc_official():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "synthetic" in readme.lower()
    assert "not" in readme.lower() and "sci-arc" in readme.lower()
