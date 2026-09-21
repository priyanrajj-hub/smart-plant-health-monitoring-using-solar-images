import traceback
import sys
sys.path.insert(0, '.')
from tests.test_pipeline import test_match_place_thresholds

try:
    test_match_place_thresholds()
    print("SUCCESS")
except Exception as e:
    traceback.print_exc()
