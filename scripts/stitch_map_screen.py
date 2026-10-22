"""
Stitch Map Screen Downloader and Metadata Record.
Records the Google Stitch project, screen asset identifiers, and handles fetching
the official Stitch generated high-fidelity Screen for the Western Sichuan Alpine Topo Map.
"""

import os
import urllib.request
import json

PROJECT_ID = "1926773866906178772"
SCREEN_ID = "31e67653cc804dd9a4d4f84e0df47a53"
SCREEN_RESOURCE_NAME = f"projects/{PROJECT_ID}/screens/{SCREEN_ID}"
DESIGN_SYSTEM_ID = "assets/b9bc4ce9ab7d44c5a83cc574484442de"

HTML_DOWNLOAD_URL = (
    "https://contribution.usercontent.google.com/download?"
    "c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sX2NiNzNkMzNkOWI1ODRlZDBiYjgyZGUyMDE0MGUwYzcyEgsSBxDOtYjGpgQYAZIBIwoKcHJvamVjdF9pZBIVQhMxOTI2NzczODY2OTA2MTc4Nzcy&filename=&opi=96797242"
)

SCREENSHOT_URL = (
    "https://lh3.googleusercontent.com/aida/AEtjO1USUrknky5awgwP6JKY3pfBWxC8TsiSPz4l4Zlu_79SRVzOMRz6LdjUjQfSQVd0vbJpr2f6lCplUY_fb-kfkE-qSAmQgUY1MgktG-pvLLtuq7971QJIhxL3WmJahfi9BTxNijZPHnWi3w2m5iJNPeh_9gv7H2bJzLllsmca7lvJ0iceSraBos0ZWickI-ZXhcPMKRJ8dBAOUtQGImi0aq7iqHGJXQGTEbnm-YQ9krZq87AnD_X6s7SASg"
)

PROMPT = (
    "Mobile outdoor exploration app home screen. High-contrast obsidian dark theme (#090d16) "
    "with aurora green accents (#4edea3) and glacial cyan (#4cd7f6). "
    "Full-screen typography/topography map of Western Sichuan with mountain cluster markers. "
    "Floating glassmorphism search bar at the top with difficulty filter chips. "
    "Bottom sheet drawer with drag handle, displaying swipeable Hero mountain cards with full-width photography, "
    "weather badge, altitude, ascent, distance, and driving hours. "
    "Bottom navigation bar with 3 tabs: Explore, Plan, Profile."
)


def fetch_and_save_screen(output_path: str = "scratch/stitch_map_screen.html") -> int:
    """Download the official Stitch screen HTML into output_path and return file size."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    urllib.request.urlretrieve(HTML_DOWNLOAD_URL, output_path)
    file_size = os.path.getsize(output_path)
    print(f"[Stitch] Downloaded {output_path} ({file_size} bytes)")
    return file_size


if __name__ == "__main__":
    print(f"Project ID: {PROJECT_ID}")
    print(f"Screen ID: {SCREEN_ID}")
    print(f"Design System: {DESIGN_SYSTEM_ID}")
    fetch_and_save_screen()
