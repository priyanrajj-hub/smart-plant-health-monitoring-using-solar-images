import json
from shapely.geometry import shape, Point
from pyproj import Geod

geod = Geod(ellps="WGS84")

def calculate_iou(poly1_geojson, poly2_geojson):
    p1 = shape(json.loads(poly1_geojson))
    p2 = shape(json.loads(poly2_geojson))
    if not p1.is_valid or not p2.is_valid:
        return 0.0
    
    intersection = p1.intersection(p2).area
    union = p1.union(p2).area
    return intersection / union if union > 0 else 0.0

def calculate_centroid_distance(lat1, lon1, lat2, lon2):
    _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
    return distance

def match_place(new_polygon_geojson, new_lat, new_lon, existing_places):
    """
    Matches a new polygon against existing places.
    Rules: IoU >= 0.6 OR centroid distance < 30m.
    existing_places: dict of {place_id: place_dict}
    Returns: matched place_id or None
    """
    for pid, place in existing_places.items():
        # Check distance
        dist = calculate_centroid_distance(new_lat, new_lon, place['centroid_lat'], place['centroid_lon'])
        if dist < 30.0:
            return pid
            
        # Check IoU
        try:
            iou = calculate_iou(new_polygon_geojson, place.get('polygon_geojson', '{}'))
            if iou >= 0.6:
                return pid
        except:
            continue
            
    return None

if __name__ == "__main__":
    p1 = '{"type": "Polygon", "coordinates": [[[0,0], [1,0], [1,1], [0,1], [0,0]]]}'
    p2 = '{"type": "Polygon", "coordinates": [[[0,0], [1.1,0], [1.1,1], [0,1], [0,0]]]}'
    print(f"Test IoU: {calculate_iou(p1, p2)}")
    print(f"Test Dist: {calculate_centroid_distance(10.0, 78.0, 10.0001, 78.0)}")
