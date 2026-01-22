import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Restaurant, MenuItem


class Command(BaseCommand):
    help = 'Import restaurants and menu items from CSV'

    def add_arguments(self, parser):
        parser.add_argument('--restaurants', type=str, help='Path to restaurants CSV')
        parser.add_argument('--items', type=str, help='Path to menu items CSV')
        parser.add_argument('--clear', action='store_true', help='Clear existing data')

    def handle(self, *args, **options):
        if options['clear']:
            MenuItem.objects.all().delete()
            Restaurant.objects.all().delete()
            self.stdout.write('Cleared existing data')

        if options['restaurants']:
            self._import_restaurants(options['restaurants'])

        if options['items']:
            self._import_items(options['items'])

        for r in Restaurant.objects.all():
            r.update_item_count()

        self.stdout.write(self.style.SUCCESS('Import complete'))

    def _import_restaurants(self, path):
        count = 0
        with open(path, 'r') as f:
            for row in csv.DictReader(f):
                Restaurant.objects.update_or_create(
                    slug=row['slug'],
                    defaults={
                        'name': row['name'],
                        'website_url': row.get('website_url', ''),
                        'logo_url': row.get('logo_url', ''),
                        'nutrition_source_url': row.get('nutrition_source_url', ''),
                        'last_updated': timezone.now(),
                    }
                )
                count += 1
        self.stdout.write(f'Imported {count} restaurants')

    def _import_items(self, path):
        count = 0
        with open(path, 'r') as f:
            for row in csv.DictReader(f):
                try:
                    restaurant = Restaurant.objects.get(slug=row['restaurant_slug'])
                    MenuItem.objects.update_or_create(
                        restaurant=restaurant,
                        name=row['name'],
                        defaults={
                            'category': row.get('category', ''),
                            'serving_size': row.get('serving_size', ''),
                            'calories': int(row['calories']),
                            'protein': Decimal(row['protein']),
                            'carbs': Decimal(row['carbs']),
                            'fat': Decimal(row['fat']),
                            'fiber': Decimal(row['fiber']) if row.get('fiber') else None,
                            'sodium': int(row['sodium']) if row.get('sodium') else None,
                            'sugar': Decimal(row['sugar']) if row.get('sugar') else None,
                            'is_vegetarian': row.get('is_vegetarian', '').lower() == 'true',
                            'is_vegan': row.get('is_vegan', '').lower() == 'true',
                            'is_gluten_free': row.get('is_gluten_free', '').lower() == 'true',
                            'source_url': row.get('source_url', ''),
                            'last_verified': timezone.now(),
                        }
                    )
                    count += 1
                except Restaurant.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Restaurant not found: {row.get('restaurant_slug')}"))
        self.stdout.write(f'Imported {count} menu items')
