from django.core.management.base import BaseCommand
from config.models import FilterConfiguration, QuickFilter, SortOption, AppConfiguration


class Command(BaseCommand):
    help = 'Seeds initial configuration data for the Graze app'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding configuration data...')

        # Clear existing data
        FilterConfiguration.objects.all().delete()
        QuickFilter.objects.all().delete()
        SortOption.objects.all().delete()

        # Seed Filter Configurations
        self.stdout.write('Creating filter configurations...')

        FilterConfiguration.objects.create(
            name='calories',
            label='Calories',
            unit='kcal',
            order=1,
            options=[
                {'label': 'Any', 'min': 0, 'max': None},
                {'label': 'Under 300', 'min': 0, 'max': 300},
                {'label': '300-500', 'min': 300, 'max': 500},
                {'label': '500-700', 'min': 500, 'max': 700},
                {'label': 'Over 700', 'min': 700, 'max': None}
            ]
        )

        FilterConfiguration.objects.create(
            name='protein',
            label='Protein',
            unit='g',
            order=2,
            options=[
                {'label': 'Any', 'min': 0, 'max': None},
                {'label': 'Under 20g', 'min': 0, 'max': 20},
                {'label': '20-40g', 'min': 20, 'max': 40},
                {'label': '40-60g', 'min': 40, 'max': 60},
                {'label': 'Over 60g', 'min': 60, 'max': None}
            ]
        )

        FilterConfiguration.objects.create(
            name='carbs',
            label='Carbs',
            unit='g',
            order=3,
            options=[
                {'label': 'Any', 'min': 0, 'max': None},
                {'label': 'Under 20g', 'min': 0, 'max': 20},
                {'label': '20-40g', 'min': 20, 'max': 40},
                {'label': '40-60g', 'min': 40, 'max': 60},
                {'label': 'Over 60g', 'min': 60, 'max': None}
            ]
        )

        FilterConfiguration.objects.create(
            name='fat',
            label='Fat',
            unit='g',
            order=4,
            options=[
                {'label': 'Any', 'min': 0, 'max': None},
                {'label': 'Under 10g', 'min': 0, 'max': 10},
                {'label': '10-20g', 'min': 10, 'max': 20},
                {'label': '20-30g', 'min': 20, 'max': 30},
                {'label': 'Over 30g', 'min': 30, 'max': None}
            ]
        )

        self.stdout.write(self.style.SUCCESS('✓ Created 4 filter configurations'))

        # Seed Quick Filters
        self.stdout.write('Creating quick filters...')

        QuickFilter.objects.create(
            name='high_protein',
            label='High Protein',
            icon='Zap',
            description='High protein dishes (40g+)',
            requires_location=False,
            order=1,
            filter_params={
                'protein': {'min': 40, 'max': None},
                'sort': 'protein_ratio_desc'
            }
        )

        QuickFilter.objects.create(
            name='low_carb',
            label='Low Carb',
            icon='TrendingDown',
            description='Low carbohydrate options (under 20g)',
            requires_location=False,
            order=2,
            filter_params={
                'carbs': {'min': 0, 'max': 20},
                'sort': 'carbs_asc'
            }
        )

        QuickFilter.objects.create(
            name='balanced',
            label='Balanced',
            icon='Scale',
            description='Balanced nutrition (30-40g protein, under 500 cal)',
            requires_location=False,
            order=3,
            filter_params={
                'protein': {'min': 30, 'max': 40},
                'calories': {'min': 0, 'max': 500},
                'sort': 'protein_ratio_desc'
            }
        )

        QuickFilter.objects.create(
            name='light',
            label='Light & Lean',
            icon='Feather',
            description='Light meals (under 300 calories)',
            requires_location=False,
            order=4,
            filter_params={
                'calories': {'min': 0, 'max': 300},
                'sort': 'calories_asc'
            }
        )

        QuickFilter.objects.create(
            name='nearby_protein',
            label='Nearby High Protein',
            icon='MapPin',
            description='High protein options near you',
            requires_location=True,
            order=5,
            filter_params={
                'protein': {'min': 40, 'max': None},
                'radius': 10,
                'sort': 'distance_asc'
            }
        )

        self.stdout.write(self.style.SUCCESS('✓ Created 5 quick filters'))

        # Seed Sort Options
        self.stdout.write('Creating sort options...')

        sort_options = [
            {'value': 'protein_ratio_desc', 'label': 'Protein Ratio (High to Low)', 'order': 1},
            {'value': 'protein_ratio_asc', 'label': 'Protein Ratio (Low to High)', 'order': 2},
            {'value': 'protein_desc', 'label': 'Protein (High to Low)', 'order': 3},
            {'value': 'protein_asc', 'label': 'Protein (Low to High)', 'order': 4},
            {'value': 'calories_asc', 'label': 'Calories (Low to High)', 'order': 5},
            {'value': 'calories_desc', 'label': 'Calories (High to Low)', 'order': 6},
            {'value': 'carbs_asc', 'label': 'Carbs (Low to High)', 'order': 7},
            {'value': 'carbs_desc', 'label': 'Carbs (High to Low)', 'order': 8},
            {'value': 'fat_asc', 'label': 'Fat (Low to High)', 'order': 9},
            {'value': 'fat_desc', 'label': 'Fat (High to Low)', 'order': 10},
            {'value': 'distance_asc', 'label': 'Distance (Nearest First)', 'requires_location': True, 'order': 11},
            {'value': 'distance_desc', 'label': 'Distance (Farthest First)', 'requires_location': True, 'order': 12},
        ]

        for sort_data in sort_options:
            SortOption.objects.create(**sort_data)

        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(sort_options)} sort options'))

        # Seed App Configuration
        self.stdout.write('Creating app configuration...')

        app_config, created = AppConfiguration.objects.get_or_create(
            pk=1,
            defaults={
                'default_sort': 'protein_ratio_desc',
                'items_per_page': 20,
                'radius_options': [5, 10, 25, 50],
                'default_map_center': [-74.0060, 40.7128],  # NYC
                'default_map_zoom': 12,
                'version': 1
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created app configuration'))
        else:
            self.stdout.write(self.style.WARNING('App configuration already exists'))

        self.stdout.write(self.style.SUCCESS('\n✅ Configuration seeding complete!'))
        self.stdout.write(f'   - Filters: {FilterConfiguration.objects.count()}')
        self.stdout.write(f'   - Quick Filters: {QuickFilter.objects.count()}')
        self.stdout.write(f'   - Sort Options: {SortOption.objects.count()}')
        self.stdout.write(f'   - App Config Version: {app_config.version}')
