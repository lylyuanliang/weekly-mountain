import json
import os

def test_data():
    base = r"d:\file_save\workspace\github\weekly-mountain\src\data"
    m_path = os.path.join(base, "mountains.json")
    wp_path = os.path.join(base, "waypoints.json")
    assert os.path.exists(m_path), "mountains.json does not exist"
    assert os.path.exists(wp_path), "waypoints.json does not exist"

    # 验证 UTF-8 编码且无 BOM 头
    with open(m_path, "rb") as f:
        m_bytes = f.read(3)
        assert m_bytes != b'\xef\xbb\xbf', "mountains.json must not have UTF-8 BOM"

    with open(wp_path, "rb") as f:
        wp_bytes = f.read(3)
        assert wp_bytes != b'\xef\xbb\xbf', "waypoints.json must not have UTF-8 BOM"

    with open(m_path, "r", encoding="utf-8") as f:
        mountains = json.load(f)
    assert len(mountains) == 50, f"Expected 50 mountains, got {len(mountains)}"

    with open(wp_path, "r", encoding="utf-8") as f:
        waypoints = json.load(f)

    required_keys = ["id", "name", "altitude_m", "county_short", "difficulty", "route_detail", "tags", "best_season"]
    total_waypoints_count = 0

    for m in mountains:
        for rk in required_keys:
            assert rk in m, f"Mountain {m.get('id')} missing required field: {rk}"
            assert m[rk] is not None, f"Mountain {m.get('id')} field {rk} is None"

        assert isinstance(m["altitude_m"], (int, float)) and m["altitude_m"] > 0, f"Invalid altitude_m for {m['id']}"
        assert m["id"] in waypoints, f"Mountain {m['id']} missing from waypoints dictionary"

        pts = waypoints[m["id"]]
        assert isinstance(pts, list) and len(pts) > 0, f"Mountain {m['id']} has no waypoints in waypoints.json"

        for pt in pts:
            total_waypoints_count += 1
            assert "name" in pt and pt["name"], f"Waypoint missing name in {m['id']}"
            assert "lat" in pt and isinstance(pt["lat"], (int, float)) and 20 <= pt["lat"] <= 40, f"Invalid lat in {m['id']}: {pt.get('lat')}"
            assert "lng" in pt and isinstance(pt["lng"], (int, float)) and 95 <= pt["lng"] <= 110, f"Invalid lng in {m['id']}: {pt.get('lng')}"
            assert "unc" in pt and isinstance(pt["unc"], bool), f"Invalid unc in {m['id']}: {pt.get('unc')}"

    assert total_waypoints_count == 387, f"Expected 387 total waypoints, got {total_waypoints_count}"

    print(f"PASS: mountains.json is 100% valid with 50 items and {len(waypoints)} waypoint sets ({total_waypoints_count} total GPS points)")

if __name__ == "__main__":
    test_data()
