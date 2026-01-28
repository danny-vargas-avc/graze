"""Tests for Graze API location endpoints."""
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import Restaurant, RestaurantLocation, LocationFlag


class LocationListViewTests(TestCase):
    """Tests for GET /api/v1/locations endpoint."""

    def setUp(self):
        self.client = APIClient()

        # Create test restaurant
        self.restaurant = Restaurant.objects.create(
            name='Test Chipotle',
            slug='chipotle'
        )

        # Create test locations in San Francisco area
        # Location 1: Downtown SF (37.7749, -122.4194)
        self.location1 = RestaurantLocation.objects.create(
            restaurant=self.restaurant,
            name='Chipotle - Downtown SF',
            latitude=Decimal('37.7749'),
            longitude=Decimal('-122.4194'),
            city='San Francisco',
            state='CA',
            is_active=True
        )

        # Location 2: Mission District (37.7599, -122.4148)
        self.location2 = RestaurantLocation.objects.create(
            restaurant=self.restaurant,
            name='Chipotle - Mission',
            latitude=Decimal('37.7599'),
            longitude=Decimal('-122.4148'),
            city='San Francisco',
            state='CA',
            is_active=True
        )

        # Location 3: Far away - Oakland (37.8044, -122.2712)
        self.location3 = RestaurantLocation.objects.create(
            restaurant=self.restaurant,
            name='Chipotle - Oakland',
            latitude=Decimal('37.8044'),
            longitude=Decimal('-122.2712'),
            city='Oakland',
            state='CA',
            is_active=True
        )

        # Location 4: Inactive location (should be filtered out)
        self.location4 = RestaurantLocation.objects.create(
            restaurant=self.restaurant,
            name='Chipotle - Closed',
            latitude=Decimal('37.7000'),
            longitude=Decimal('-122.4000'),
            city='San Francisco',
            state='CA',
            is_active=False
        )

    def test_list_all_locations(self):
        """Test listing all active locations without filters."""
        response = self.client.get('/api/v1/locations')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)
        self.assertEqual(response.data['meta']['total'], 3)
        self.assertEqual(response.data['meta']['limit'], 100)

    def test_bbox_filtering(self):
        """Test filtering locations by bounding box."""
        # Bounding box that only includes downtown SF and Mission
        bbox = '37.75,-122.43,37.78,-122.41'
        response = self.client.get(f'/api/v1/locations?bbox={bbox}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)

        # Check that Oakland location is excluded
        names = [loc['name'] for loc in response.data['data']]
        self.assertIn('Chipotle - Downtown SF', names)
        self.assertIn('Chipotle - Mission', names)
        self.assertNotIn('Chipotle - Oakland', names)

    def test_radius_filtering(self):
        """Test filtering locations by radius from user location."""
        # Center point near downtown SF
        lat, lng = '37.7749', '-122.4194'
        radius = '1'  # 1 mile radius

        response = self.client.get(f'/api/v1/locations?lat={lat}&lng={lng}&radius={radius}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only get locations within 1 mile
        self.assertLessEqual(len(response.data['data']), 3)
        self.assertEqual(response.data['meta']['center_lat'], 37.7749)
        self.assertEqual(response.data['meta']['center_lng'], -122.4194)
        self.assertEqual(response.data['meta']['radius_miles'], 1.0)

    def test_distance_calculation(self):
        """Test that distance is calculated correctly when lat/lng provided."""
        lat, lng = '37.7749', '-122.4194'

        response = self.client.get(f'/api/v1/locations?lat={lat}&lng={lng}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that distance_miles is present in response
        for location in response.data['data']:
            self.assertIn('distance_miles', location)
            self.assertIsNotNone(location['distance_miles'])

        # Verify ordering by distance (closest first)
        distances = [loc['distance_miles'] for loc in response.data['data']]
        self.assertEqual(distances, sorted(distances))

    def test_restaurant_filtering(self):
        """Test filtering locations by restaurant slug."""
        # Create another restaurant
        other_restaurant = Restaurant.objects.create(
            name='Test Cava',
            slug='cava'
        )
        RestaurantLocation.objects.create(
            restaurant=other_restaurant,
            name='Cava - SF',
            latitude=Decimal('37.7800'),
            longitude=Decimal('-122.4100'),
            city='San Francisco',
            state='CA',
            is_active=True
        )

        response = self.client.get('/api/v1/locations?restaurants=chipotle')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3)

        # All should be Chipotle
        for location in response.data['data']:
            self.assertEqual(location['restaurant']['slug'], 'chipotle')

    def test_limit_parameter(self):
        """Test limiting number of results."""
        response = self.client.get('/api/v1/locations?limit=2')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
        self.assertEqual(response.data['meta']['limit'], 2)
        self.assertEqual(response.data['meta']['total'], 3)

    def test_invalid_bbox(self):
        """Test error handling for invalid bounding box."""
        response = self.client.get('/api/v1/locations?bbox=invalid')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('bbox', response.data)


class LocationDetailViewTests(TestCase):
    """Tests for GET /api/v1/locations/<id> endpoint."""

    def setUp(self):
        self.client = APIClient()

        self.restaurant = Restaurant.objects.create(
            name='Test Chipotle',
            slug='chipotle'
        )

        self.location = RestaurantLocation.objects.create(
            restaurant=self.restaurant,
            name='Chipotle - Downtown SF',
            latitude=Decimal('37.7749'),
            longitude=Decimal('-122.4194'),
            address='123 Market St',
            city='San Francisco',
            state='CA',
            postcode='94103',
            is_active=True,
            data_source='osm'
        )

    def test_get_location_detail(self):
        """Test retrieving detailed location information."""
        response = self.client.get(f'/api/v1/locations/{self.location.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Chipotle - Downtown SF')
        self.assertEqual(response.data['city'], 'San Francisco')
        self.assertEqual(response.data['state'], 'CA')
        self.assertEqual(response.data['address'], '123 Market St')
        self.assertEqual(response.data['data_source'], 'osm')
        self.assertIn('restaurant', response.data)

    def test_get_nonexistent_location(self):
        """Test 404 for nonexistent location."""
        response = self.client.get('/api/v1/locations/99999')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_inactive_location_not_accessible(self):
        """Test that inactive locations return 404."""
        inactive_location = RestaurantLocation.objects.create(
            restaurant=self.restaurant,
            name='Chipotle - Closed',
            latitude=Decimal('37.7000'),
            longitude=Decimal('-122.4000'),
            city='San Francisco',
            state='CA',
            is_active=False
        )

        response = self.client.get(f'/api/v1/locations/{inactive_location.id}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LocationFlagCreateViewTests(TestCase):
    """Tests for POST /api/v1/location-flags endpoint."""

    def setUp(self):
        self.client = APIClient()

        self.restaurant = Restaurant.objects.create(
            name='Test Chipotle',
            slug='chipotle'
        )

        self.location = RestaurantLocation.objects.create(
            restaurant=self.restaurant,
            name='Chipotle - Downtown SF',
            latitude=Decimal('37.7749'),
            longitude=Decimal('-122.4194'),
            city='San Francisco',
            state='CA',
            is_active=True
        )

    def test_create_location_flag(self):
        """Test creating a location flag."""
        data = {
            'location': self.location.id,
            'flag_type': 'closed',
            'user_comment': 'This location is permanently closed'
        }

        response = self.client.post('/api/v1/location-flags', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Thank you for reporting this location issue.')

        # Verify flag was created
        flag = LocationFlag.objects.get(location=self.location)
        self.assertEqual(flag.flag_type, 'closed')
        self.assertEqual(flag.user_comment, 'This location is permanently closed')
        self.assertIsNotNone(flag.user_ip)
        self.assertFalse(flag.resolved)

    def test_create_flag_without_comment(self):
        """Test creating a flag without optional comment."""
        data = {
            'location': self.location.id,
            'flag_type': 'wrong_address'
        }

        response = self.client.post('/api/v1/location-flags', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        flag = LocationFlag.objects.get(location=self.location)
        self.assertEqual(flag.user_comment, '')

    def test_create_flag_invalid_type(self):
        """Test error handling for invalid flag type."""
        data = {
            'location': self.location.id,
            'flag_type': 'invalid_type',
            'user_comment': 'Test'
        }

        response = self.client.post('/api/v1/location-flags', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_flag_missing_location(self):
        """Test error handling for missing location."""
        data = {
            'flag_type': 'closed',
            'user_comment': 'Test'
        }

        response = self.client.post('/api/v1/location-flags', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
