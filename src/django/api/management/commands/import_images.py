import csv
from django.core.management.base import BaseCommand
from api.models import Restaurant, MenuItem


class Command(BaseCommand):
    help = 'Import image URLs for menu items from CSV (columns: name, image_url)'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to CSV with name,image_url columns')
        parser.add_argument('--restaurant', type=str, required=True, help='Restaurant slug')

    def handle(self, *args, **options):
        slug = options['restaurant']
        try:
            restaurant = Restaurant.objects.get(slug=slug)
        except Restaurant.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Restaurant not found: {slug}'))
            return

        updated = 0
        not_found = []

        with open(options['csv_path'], 'r') as f:
            for row in csv.DictReader(f):
                name = row['name'].strip()
                image_url = row['image_url'].strip()

                matched = MenuItem.objects.filter(restaurant=restaurant, name=name)
                if matched.exists():
                    matched.update(image_url=image_url)
                    updated += matched.count()
                else:
                    not_found.append(name)

        self.stdout.write(self.style.SUCCESS(f'Updated {updated} items for {restaurant.name}'))
        if not_found:
            self.stdout.write(self.style.WARNING(f'Not found in DB ({len(not_found)}):'))
            for name in not_found:
                self.stdout.write(f'  - {name}')
