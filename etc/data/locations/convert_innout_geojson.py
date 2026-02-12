"""Convert In-N-Out GeoJSON data from GitHub to CSV format for import."""

import csv
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, "innout_github.geojson")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "in_n_out_all_locations.csv")

CSV_HEADERS = [
    "osm_id",
    "osm_type",
    "name",
    "brand",
    "latitude",
    "longitude",
    "address",
    "city",
    "state",
    "postcode",
    "phone",
    "website",
    "opening_hours",
    "amenity_type",
    "cuisine",
]

OSM_ID_START = 9900001


def convert():
    with open(INPUT_FILE) as f:
        geojson = json.load(f)

    features = geojson["features"]
    print(f"Loaded {len(features)} features from {INPUT_FILE}")

    rows = []
    for i, feature in enumerate(features):
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]

        longitude = coords[0]
        latitude = coords[1]

        # Build opening hours from drive-thru and dining room hours
        drive_thru = props.get("DriveThruHours", "")
        dining_room = props.get("DiningRoomHours", "")
        opening_hours = ""
        if drive_thru:
            opening_hours = drive_thru

        # Use ZipCode, converting int to string and zero-padding to 5 digits
        zipcode = props.get("ZipCode")
        if zipcode is not None:
            postcode = str(int(zipcode)).zfill(5)
        else:
            postcode = ""

        row = {
            "osm_id": OSM_ID_START + i,
            "osm_type": "",
            "name": f"In-N-Out Burger - {props.get('Name', '')}",
            "brand": "In-N-Out Burger",
            "latitude": latitude,
            "longitude": longitude,
            "address": props.get("StreetAddress", ""),
            "city": props.get("City", ""),
            "state": props.get("State", ""),
            "postcode": postcode,
            "phone": "",
            "website": "https://www.in-n-out.com",
            "opening_hours": opening_hours,
            "amenity_type": "fast_food",
            "cuisine": "burger",
        }
        rows.append(row)

    # Sort by state then city for readability
    rows.sort(key=lambda r: (r["state"], r["city"], r["address"]))

    # Reassign OSM IDs after sorting so they're sequential by state/city
    for i, row in enumerate(rows):
        row["osm_id"] = OSM_ID_START + i

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} locations to {OUTPUT_FILE}")

    # Summary by state
    from collections import Counter
    states = Counter(r["state"] for r in rows)
    for state, count in sorted(states.items()):
        print(f"  {state}: {count}")


if __name__ == "__main__":
    convert()
