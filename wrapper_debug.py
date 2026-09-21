import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    import tests.test_pipeline
    print("IMPORT OK!")
except Exception as e:
    print("IMPORT FAILED!")
    traceback.print_exc()
