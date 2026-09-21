import sys
import os
import pytest
import traceback

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("Testing importing from scripts...")
    try:
        import scripts.place_matching
        import ml.models.stress_tabular
        print("Imports Successful. Running pytest...")
        pytest.main(["-v", "tests/test_pipeline.py"])
    except Exception as e:
        print("Import Failed!")
        traceback.print_exc()
