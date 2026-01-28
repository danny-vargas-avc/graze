#!/usr/bin/env python3
"""
Chipotle Official API Scraper

Uses Chipotle's public store locator API to get all US locations.
Should retrieve ~4,000 locations (vs 2,152 from OpenStreetMap).

API Endpoint: https://services.chipotle.com/restaurant/api/v2.1/search
"""

import requests
import json
import csv
import time
from datetime import datetime
from typing import List, Dict


class ChipotleAPIScraper:
    """Scraper for Chipotle locations using their official API"""

    BASE_URL = "https://services.chipotle.com/restaurant/api/v2.1/search"

    # Major US cities to use as search centers to cover all locations
    # Using large radius searches from these points should capture all stores
    SEARCH_CENTERS = [
        {"lat": 40.7128, "lng": -74.0060, "name": "New York"},
        {"lat": 34.0522, "lng": -118.2437, "name": "Los Angeles"},
        {"lat": 41.8781, "lng": -87.6298, "name": "Chicago"},
        {"lat": 29.7604, "lng": -95.3698, "name": "Houston"},
        {"lat": 33.4484, "lng": -112.0740, "name": "Phoenix"},
        {"lat": 39.7392, "lng": -104.9903, "name": "Denver"},
        {"lat": 47.6062, "lng": -122.3321, "name": "Seattle"},
        {"lat": 37.7749, "lng": -122.4194, "name": "San Francisco"},
        {"lat": 32.7767, "lng": -96.7970, "name": "Dallas"},
        {"lat": 25.7617, "lng": -80.1918, "name": "Miami"},
        {"lat": 42.3601, "lng": -71.0589, "name": "Boston"},
        {"lat": 33.7490, "lng": -84.3880, "name": "Atlanta"},
    ]

    def __init__(self):
        self.locations = []
        self.seen_ids = set()  # Deduplicate across searches

    def search_area(self, lat: float, lng: float, radius: int = 9999999) -> List[Dict]:
        """Search for Chipotle locations within radius (in miles) of lat/lng"""

        # Using POST method with JSON payload (from working 2020 scraper)
        payload = {
            'latitude': lat,
            'longitude': lng,
            'radius': radius,  # Large radius to get all locations
            'pageSize': 5000,  # Max results
            'restaurantStatuses': ['OPEN', 'LAB'],
            'conceptIds': ['CMG']
        }

        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/json',
            # Subscription key from 2020 tutorial - may not work anymore
            'Ocp-Apim-Subscription-Key': 'b4d9f36380184a3788857063bce25d6a'
        }

        try:
            response = requests.post(
                self.BASE_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            restaurants = data.get('data', [])
            return restaurants

        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error fetching data: {e}")
            return []

    def parse_location(self, restaurant: Dict) -> Dict:
        """Parse API response into structured location data"""

        # Extract address components
        addresses = restaurant.get('addresses', [{}])
        address_data = addresses[0] if addresses else {}

        location = {
            'restaurant_number': restaurant.get('restaurantNumber', ''),
            'name': restaurant.get('restaurantName', 'Chipotle'),
            'latitude': restaurant.get('latitude'),
            'longitude': restaurant.get('longitude'),
            'address': address_data.get('addressLine1', ''),
            'city': address_data.get('locality', ''),
            'state': address_data.get('administrativeArea', ''),
            'postcode': address_data.get('postalCode', ''),
            'phone': restaurant.get('telephone', ''),
            'website': restaurant.get('url', ''),
            'status': restaurant.get('restaurantStatus', ''),
            'is_active': restaurant.get('isActive', False),
            'real_estate_category': restaurant.get('realEstateCategory', ''),
        }

        return location

    def scrape(self) -> List[Dict]:
        """Main scraping method - single nationwide search"""
        print(f"Scraping Chipotle locations using official API...")
        print(f"Using nationwide search (large radius from central US)\n")

        # Use Kansas (geographic center of US) for nationwide search
        center_lat = 39.8283
        center_lng = -98.5795

        print(f"Searching nationwide...")
        restaurants = self.search_area(center_lat, center_lng)

        for restaurant in restaurants:
            restaurant_id = restaurant.get('restaurantNumber')

            if restaurant_id and restaurant_id not in self.seen_ids:
                self.seen_ids.add(restaurant_id)
                location = self.parse_location(restaurant)
                self.locations.append(location)

        print(f"✓ Total unique locations found: {len(self.locations)}")
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
                'chain': 'Chipotle',
                'country': 'US',
                'scraped_at': datetime.now().isoformat(),
                'total_locations': len(self.locations),
                'source': 'Chipotle Official API',
                'api_endpoint': self.BASE_URL
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
        print(f"SUMMARY: Chipotle Locations (Official API)")
        print(f"{'='*60}")
        print(f"Total locations found: {len(self.locations)}")

        # Count active vs inactive
        active = sum(1 for loc in self.locations if loc['is_active'])
        print(f"Active locations: {active}")
        print(f"Inactive locations: {len(self.locations) - active}")

        # Count locations with complete data
        with_address = sum(1 for loc in self.locations if loc['address'])
        with_phone = sum(1 for loc in self.locations if loc['phone'])
        with_city = sum(1 for loc in self.locations if loc['city'])
        with_state = sum(1 for loc in self.locations if loc['state'])

        print(f"\nData Completeness:")
        print(f"  - With street address: {with_address} ({with_address/len(self.locations)*100:.1f}%)")
        print(f"  - With city: {with_city} ({with_city/len(self.locations)*100:.1f}%)")
        print(f"  - With state: {with_state} ({with_state/len(self.locations)*100:.1f}%)")
        print(f"  - With phone: {with_phone} ({with_phone/len(self.locations)*100:.1f}%)")

        # Show sample locations
        print(f"\nSample Locations (first 5):")
        for i, loc in enumerate(self.locations[:5], 1):
            print(f"\n  {i}. {loc['name']} (#{loc['restaurant_number']})")
            print(f"     Address: {loc['address']}, {loc['city']}, {loc['state']} {loc['postcode']}")
            print(f"     Coords: {loc['latitude']}, {loc['longitude']}")
            print(f"     Phone: {loc['phone'] or 'N/A'}")
            print(f"     Status: {loc['status']}, Active: {loc['is_active']}")

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
    print("Chipotle Official API Scraper")
    print("="*60 + "\n")

    # Create scraper
    scraper = ChipotleAPIScraper()

    # Scrape locations
    locations = scraper.scrape()

    if locations:
        # Generate filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = f"../data/chipotle_api_locations_{timestamp}.csv"
        json_file = f"../data/chipotle_api_locations_{timestamp}.json"

        # Save data
        scraper.save_to_csv(csv_file)
        scraper.save_to_json(json_file)

        # Print summary
        scraper.print_summary()

        print(f"Comparison:")
        print(f"  - OpenStreetMap: 2,152 locations (54% coverage)")
        print(f"  - Official API: {len(locations)} locations")
        print(f"  - Expected: ~3,938 locations (from ScrapeHero)")
    else:
        print("\n✗ No locations found. Check API endpoint or network connection.")


if __name__ == '__main__':
    main()
