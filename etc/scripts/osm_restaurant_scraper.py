
#!/usr/bin/env python3
"""
OpenStreetMap Restaurant Location Scraper - Proof of Concept

Queries OpenStreetMap Overpass API to extract restaurant chain locations.
Outputs data to CSV and JSON for quality assessment.

Usage:
    python osm_restaurant_scraper.py --chain "Chipotle" --country US
"""

import requests
import json
import csv
import argparse
from datetime import datetime
from typing import List, Dict, Optional


class OSMRestaurantScraper:
    """Scraper for restaurant locations from OpenStreetMap"""

    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    def __init__(self, chain_name: str, country_code: str = "US"):
        self.chain_name = chain_name
        self.country_code = country_code
        self.locations = []

    def build_query(self) -> str:
        """Build Overpass QL query for restaurant chain"""
        # Query searches for nodes and ways (buildings) with matching name
        # Searches in: amenity=restaurant, amenity=fast_food, shop=restaurant
        query = f"""
        [out:json][timeout:60];
        area["ISO3166-1"="{self.country_code}"][admin_level=2];
        (
          node(area)[name~"{self.chain_name}",i]["amenity"~"restaurant|fast_food"];
          way(area)[name~"{self.chain_name}",i]["amenity"~"restaurant|fast_food"];
        );
        out center;
        out tags;
        """
        return query

    def fetch_locations(self) -> List[Dict]:
        """Fetch locations from Overpass API"""
        print(f"Querying OpenStreetMap for '{self.chain_name}' locations in {self.country_code}...")

        query = self.build_query()

        try:
            response = requests.post(
                self.OVERPASS_URL,
                data={'data': query},
                timeout=90
            )
            response.raise_for_status()
            data = response.json()

            elements = data.get('elements', [])
            print(f"✓ Found {len(elements)} potential locations")

            return elements

        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching data: {e}")
            return []

    def parse_location(self, element: Dict) -> Optional[Dict]:
        """Parse OSM element into structured location data"""
        tags = element.get('tags', {})

        # Get coordinates (nodes have lat/lng directly, ways have center)
        if element['type'] == 'node':
            lat = element.get('lat')
            lng = element.get('lon')
        elif element['type'] == 'way':
            center = element.get('center', {})
            lat = center.get('lat')
            lng = center.get('lon')
        else:
            return None

        if not lat or not lng:
            return None

        # Extract location data
        location = {
            'osm_id': element.get('id'),
            'osm_type': element['type'],
            'name': tags.get('name', ''),
            'brand': tags.get('brand', ''),
            'latitude': lat,
            'longitude': lng,
            'address': tags.get('addr:street', ''),
            'city': tags.get('addr:city', ''),
            'state': tags.get('addr:state', ''),
            'postcode': tags.get('addr:postcode', ''),
            'phone': tags.get('phone', ''),
            'website': tags.get('website', ''),
            'opening_hours': tags.get('opening_hours', ''),
            'amenity_type': tags.get('amenity', ''),
            'cuisine': tags.get('cuisine', ''),
        }

        return location

    def scrape(self) -> List[Dict]:
        """Main scraping method"""
        elements = self.fetch_locations()

        print(f"\nParsing location data...")
        for element in elements:
            location = self.parse_location(element)
            if location:
                self.locations.append(location)

        print(f"✓ Successfully parsed {len(self.locations)} locations")
        return self.locations

    def save_to_csv(self, filename: str):
        """Save locations to CSV file"""
        if not self.locations:
            print("No locations to save")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.locations[0].keys())
            writer.writeheader()
            writer.writerows(self.locations)

        print(f"✓ Saved {len(self.locations)} locations to {filename}")

    def save_to_json(self, filename: str):
        """Save locations to JSON file"""
        if not self.locations:
            print("No locations to save")
            return

        output = {
            'metadata': {
                'chain': self.chain_name,
                'country': self.country_code,
                'scraped_at': datetime.now().isoformat(),
                'total_locations': len(self.locations),
                'source': 'OpenStreetMap Overpass API'
            },
            'locations': self.locations
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved {len(self.locations)} locations to {filename}")

    def print_summary(self):
        """Print summary statistics"""
        if not self.locations:
            print("\nNo locations found")
            return

        print(f"\n{'='*60}")
        print(f"SUMMARY: {self.chain_name} Locations")
        print(f"{'='*60}")
        print(f"Total locations found: {len(self.locations)}")

        # Count locations with complete data
        with_address = sum(1 for loc in self.locations if loc['address'])
        with_phone = sum(1 for loc in self.locations if loc['phone'])
        with_hours = sum(1 for loc in self.locations if loc['opening_hours'])
        with_city = sum(1 for loc in self.locations if loc['city'])
        with_state = sum(1 for loc in self.locations if loc['state'])

        print(f"\nData Completeness:")
        print(f"  - With street address: {with_address} ({with_address/len(self.locations)*100:.1f}%)")
        print(f"  - With city: {with_city} ({with_city/len(self.locations)*100:.1f}%)")
        print(f"  - With state: {with_state} ({with_state/len(self.locations)*100:.1f}%)")
        print(f"  - With phone: {with_phone} ({with_phone/len(self.locations)*100:.1f}%)")
        print(f"  - With hours: {with_hours} ({with_hours/len(self.locations)*100:.1f}%)")

        # Show sample locations
        print(f"\nSample Locations (first 5):")
        for i, loc in enumerate(self.locations[:5], 1):
            print(f"\n  {i}. {loc['name']}")
            print(f"     Address: {loc['address']}, {loc['city']}, {loc['state']} {loc['postcode']}")
            print(f"     Coords: {loc['latitude']}, {loc['longitude']}")
            print(f"     Phone: {loc['phone'] or 'N/A'}")

        # State distribution
        states = {}
        for loc in self.locations:
            state = loc.get('state', 'Unknown')
            states[state] = states.get(state, 0) + 1

        print(f"\nTop 10 States by Location Count:")
        for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {state}: {count}")

        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Scrape restaurant chain locations from OpenStreetMap'
    )
    parser.add_argument(
        '--chain',
        type=str,
        required=True,
        help='Restaurant chain name (e.g., "Chipotle", "Chick-fil-A")'
    )
    parser.add_argument(
        '--country',
        type=str,
        default='US',
        help='Country code (default: US)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='../data/locations',
        help='Output directory for CSV and JSON files'
    )

    args = parser.parse_args()

    # Create scraper
    scraper = OSMRestaurantScraper(args.chain, args.country)

    # Scrape locations
    locations = scraper.scrape()

    if locations:
        # Generate filenames
        chain_slug = args.chain.lower().replace(' ', '_').replace('-', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f"{args.output_dir}/{chain_slug}_locations_{timestamp}.csv"
        json_file = f"{args.output_dir}/{chain_slug}_locations_{timestamp}.json"

        # Save data
        scraper.save_to_csv(csv_file)
        scraper.save_to_json(json_file)

        # Print summary
        scraper.print_summary()
    else:
        print("\n✗ No locations found. Try adjusting the chain name or check your connection.")


if __name__ == '__main__':
    main()
