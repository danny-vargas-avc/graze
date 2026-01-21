"""
Management command to import restaurant and menu item data from CSV.
"""
import csv
from decimal import Decimal
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Restaurant, MenuItem


class Command(BaseCommand):
    help = 'Import restaurants and menu items from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--restaurants',
            type=str,
            help='Path to restaurants CSV file'
        )
        parser.add_argument(
            '--items',
            type=str,
            help='Path to menu items CSV file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            MenuItem.objects.all().delete()
            Restaurant.objects.all().delete()

        if options['restaurants']:
            self.import_restaurants(options['restaurants'])

        if options['items']:
            self.import_menu_items(options['items'])

        # Update item counts
        for restaurant in Restaurant.objects.all():
            restaurant.update_item_count()

        self.stdout.write(self.style.SUCCESS('Import complete!'))

    def import_restaurants(self, filepath):
        self.stdout.write(f'Importing restaurants from {filepath}...')
        count = 0

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
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

    def import_menu_items(self, filepath):
        self.stdout.write(f'Importing menu items from {filepath}...')
        count = 0
        errors = []

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    restaurant = Restaurant.objects.get(slug=row['restaurant_slug'])

                    # Parse optional fields
                    fiber = Decimal(row['fiber']) if row.get('fiber') else None
                    sodium = int(row['sodium']) if row.get('sodium') else None
                    sugar = Decimal(row['sugar']) if row.get('sugar') else None
                    saturated_fat = Decimal(row['saturated_fat']) if row.get('saturated_fat') else None

                    # Parse boolean fields
                    is_vegetarian = row.get('is_vegetarian', '').lower() == 'true'
                    is_vegan = row.get('is_vegan', '').lower() == 'true'
                    is_gluten_free = row.get('is_gluten_free', '').lower() == 'true'

                    # Parse array fields
                    allergens = [a.strip() for a in row.get('allergens', '').split(',') if a.strip()]
                    tags = [t.strip() for t in row.get('tags', '').split(',') if t.strip()]

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
                            'fiber': fiber,
                            'sodium': sodium,
                            'sugar': sugar,
                            'saturated_fat': saturated_fat,
                            'is_vegetarian': is_vegetarian,
                            'is_vegan': is_vegan,
                            'is_gluten_free': is_gluten_free,
                            'allergens': allergens,
                            'tags': tags,
                            'source_url': row.get('source_url', ''),
                            'last_verified': timezone.now(),
                        }
                    )
                    count += 1
                except Restaurant.DoesNotExist:
                    errors.append(f"Restaurant not found: {row.get('restaurant_slug')}")
                except Exception as e:
                    errors.append(f"Error importing {row.get('name')}: {e}")

        self.stdout.write(f'Imported {count} menu items')
        if errors:
            for error in errors[:10]:
                self.stdout.write(self.style.WARNING(error))
            if len(errors) > 10:
                self.stdout.write(self.style.WARNING(f'...and {len(errors) - 10} more errors'))
