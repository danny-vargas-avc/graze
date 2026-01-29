"""Django management command to import restaurant locations from CSV files."""
import csv
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand, CommandError
from api.models import Restaurant, RestaurantLocation


class Command(BaseCommand):
    help = 'Import restaurant locations from OpenStreetMap CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--chain',
            type=str,
            required=True,
            help='Restaurant chain name (e.g., "chipotle", "cava")'
        )
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to CSV file with location data'
        )

    def handle(self, *args, **options):
        chain_name = options['chain']
        csv_file = options['file']

        # Find restaurant by name (case-insensitive)
        try:
            restaurant = Restaurant.objects.get(name__iexact=chain_name)
        except Restaurant.DoesNotExist:
            raise CommandError(f'Restaurant "{chain_name}" not found in database. Please create it first.')

        self.stdout.write(f'Importing locations for: {restaurant.name}')

        # Parse CSV and import locations
        imported_count = 0
        skipped_count = 0
        error_count = 0

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    try:
                        osm_id = int(row['osm_id'])

                        # Skip if already exists
                        if RestaurantLocation.objects.filter(osm_id=osm_id).exists():
                            skipped_count += 1
                            continue

                        # Parse coordinates
                        try:
                            latitude = Decimal(row['latitude'])
                            longitude = Decimal(row['longitude'])
                        except (InvalidOperation, ValueError):
                            self.stderr.write(f'Invalid coordinates for OSM ID {osm_id}, skipping')
                            error_count += 1
                            continue

                        # Create location name
                        location_name = row.get('name', restaurant.name)
                        if row.get('city'):
                            location_name = f"{restaurant.name} - {row['city']}"

                        # Create RestaurantLocation
                        RestaurantLocation.objects.create(
                            restaurant=restaurant,
                            osm_id=osm_id,
                            name=location_name,
                            latitude=latitude,
                            longitude=longitude,
                            address=row.get('address', ''),
                            city=row.get('city', ''),
                            state=row.get('state', ''),
                            postcode=row.get('postcode', ''),
                            phone=row.get('phone', ''),
                            website=row.get('website', ''),
                            data_source='osm',
                            osm_amenity_type=row.get('amenity_type', ''),
                            is_active=True,
                            is_verified=False
                        )
                        imported_count += 1

                    except KeyError as e:
                        self.stderr.write(f'Missing required field {e} in CSV row, skipping')
                        error_count += 1
                        continue
                    except Exception as e:
                        self.stderr.write(f'Error importing location: {e}')
                        error_count += 1
                        continue

        except FileNotFoundError:
            raise CommandError(f'CSV file not found: {csv_file}')

        # Update restaurant location count
        restaurant.update_location_count()

        # Output summary
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\n'
            f'Import Summary for {restaurant.name}\n'
            f'{"="*60}\n'
            f'Imported: {imported_count} locations\n'
            f'Skipped (duplicates): {skipped_count} locations\n'
            f'Errors: {error_count} locations\n'
            f'Restaurant location count: {restaurant.location_count}\n'
            f'{"="*60}'
        ))
