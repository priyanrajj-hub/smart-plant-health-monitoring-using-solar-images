import traceback
import json
import sys
sys.path.insert(0, '.')
from scripts.place_matching import calculate_iou

box1 = json.dumps({'type': 'Polygon', 'coordinates': [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]})
try:
    calculate_iou(box1, box1)
    print("SUCCESS")
except Exception as e:
    traceback.print_exc()
