import traceback
from tests.test_pipeline import (
    test_place_matching_iou,
    test_match_place_thresholds,
    test_visit_counting,
    test_schema_structure,
    test_provenance_guard,
    test_spatial_leakage_groups
)

funcs = [
    test_place_matching_iou,
    test_match_place_thresholds,
    test_visit_counting,
    test_schema_structure,
    test_provenance_guard,
    test_spatial_leakage_groups
]

for f in funcs:
    try:
        f()
        print(f"{f.__name__}: PASSED")
    except Exception as e:
        print(f"{f.__name__}: FAILED - {type(e).__name__}: {str(e)}")
