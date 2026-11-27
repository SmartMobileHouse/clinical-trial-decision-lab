"""The Zenodo metadata file replaces CITATION.cff for release archiving, so it must stay complete and in step with it."""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_zenodo_metadata_is_complete_and_matches_the_citation_file() -> None:
    zenodo = json.loads((ROOT / ".zenodo.json").read_text())
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    assert zenodo["title"] == citation["title"]
    assert zenodo["upload_type"] == "software" and zenodo["access_right"] == "open" and zenodo["license"] == "mit"
    assert zenodo["keywords"] == citation["keywords"]
    names = [f"{a['family-names']}, {a['given-names']}" for a in citation["authors"]]
    assert [c["name"] for c in zenodo["creators"]] == names
    assert "version" not in zenodo  # Zenodo takes the version from the release tag
    relations = {r["relation"]: r["identifier"] for r in zenodo["related_identifiers"]}
    assert relations["isDocumentedBy"] == citation["url"]
    assert relations["isSupplementedBy"].startswith("https://huggingface.co/datasets/")
    assert zenodo["communities"] == [{"identifier": "smart-mobile-house"}]
