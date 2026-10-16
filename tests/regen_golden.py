"""Rewrite tests/golden/cafe.json from the current reference model (review the diff!)."""

import json

from engine.brief import Brief

from .conftest import CAFE_BRIEF
from .test_reference import GOLDEN, golden_values

if __name__ == "__main__":
    GOLDEN.parent.mkdir(exist_ok=True)
    GOLDEN.write_text(json.dumps(golden_values(Brief.load(CAFE_BRIEF)), indent=1) + "\n")
    print("wrote", GOLDEN)
