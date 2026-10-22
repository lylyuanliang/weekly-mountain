"""
Verification test suite for Stitch Map Screen and Design Tokens.
Validates:
1. scratch/stitch_map_screen.html exists and is > 5KB.
2. src/styles/stitch-tokens.css contains key color variables, glassmorphism, shadows, and radii.
3. Official screen HTML contains the map canvas, bottom sheet drawer, hero mountain cards, and 3-tab navigation.
"""

import os
import sys

def test_screen_file_exists_and_valid():
    html_path = os.path.join("scratch", "stitch_map_screen.html")
    assert os.path.exists(html_path), f"File {html_path} does not exist!"
    size = os.path.getsize(html_path)
    print(f"[PASS] Screen file exists. Size: {size} bytes (> 5KB)")
    assert size > 5000, f"File {html_path} is smaller than 5KB ({size} bytes)"


def test_design_tokens_css():
    css_path = os.path.join("src", "styles", "stitch-tokens.css")
    assert os.path.exists(css_path), f"File {css_path} does not exist!"
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    required_tokens = [
        "--bg-obsidian",
        "--acc-aurora",
        "--acc-cyan",
        "--acc-gold",
        "--text-primary",
        "--text-secondary",
        "--glass-bg",
        "--glass-border",
        "--glass-blur-lg",
        "--shadow-drawer",
        "--shadow-card",
        "--shadow-glow",
        "--radius-card",
        "--radius-drawer",
        "--radius-pill",
        "--font-headline",
        "--font-data",
        "frost-glass",
        "beacon-pulse",
    ]

    for token in required_tokens:
        assert token in content, f"Token or class '{token}' missing from {css_path}"
    print(f"[PASS] All {len(required_tokens)} critical design tokens and classes present in {css_path}")


def test_screen_html_structure():
    html_path = os.path.join("scratch", "stitch_map_screen.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Map Canvas and topo lines
    assert "<svg" in html, "SVG Topography map missing"
    assert "contour" in html.lower() or "peakglow" in html.lower(), "Contour elevation paths missing"

    # 2. Mountain clusters / markers
    assert "四姑娘山" in html, "Mt. Siguniang marker missing"
    assert "贡嘎山" in html, "Mt. Gongga marker missing"
    assert "牛背山" in html, "Niubeishan marker missing"
    assert "达瓦更扎" in html, "Dawa Gengzha marker missing"

    # 3. Top Floating Search & Filter chips
    assert "Search peaks, routes, GPS tracks..." in html or "search" in html.lower(), "Search bar missing"
    assert "All Peaks" in html, "Filter chip All Peaks missing"
    assert "L1 Leisure" in html, "Filter chip L1 Leisure missing"
    assert "L2 Intermediate" in html, "Filter chip L2 Intermediate missing"
    assert "L3 Summit Challenge" in html, "Filter chip L3 Summit Challenge missing"

    # 4. BottomSheet Drawer container
    assert "cursor-grab" in html or "w-12 h-1.2 rounded-full" in html or "drag" in html.lower(), "Drawer drag handle missing"
    assert "Active Peaks" in html, "Drawer Active Peaks header missing"

    # 5. Swipeable Hero Mountain Cards
    assert "四姑娘山·大峰" in html, "Hero card 1 (Siguniang Dafeng) missing"
    assert "牛背山·360°云海" in html, "Hero card 2 (Niubeishan) missing"
    assert "达瓦更扎·星空营地" in html, "Hero card 3 (Dawa Gengzha) missing"
    assert "+1200m" in html, "Elevation ascent metrics missing"
    assert "18.0km" in html, "Distance metric missing"
    assert "Add to Plan" in html, "Add to Plan button missing"

    # 6. Bottom Navigation Bar with 3 tabs
    assert "Explore" in html, "Bottom nav 'Explore' tab missing"
    assert "Plan" in html, "Bottom nav 'Plan' tab missing"
    assert "Profile" in html, "Bottom nav 'Profile' tab missing"
    assert "<nav" in html, "Navigation element missing"

    print("[PASS] Screen HTML structure successfully verified with all required containers, markers, drawer, and tabs.")


if __name__ == "__main__":
    try:
        test_screen_file_exists_and_valid()
        test_design_tokens_css()
        test_screen_html_structure()
        print("\n>>> ALL STITCH TOKEN & SCREEN TESTS PASSED! <<<")
    except AssertionError as e:
        print(f"\n[FAIL] {e}", file=sys.stderr)
        sys.exit(1)
