"""Custom admin views for CSV/PDF import workflows."""
import csv
import io
from decimal import Decimal, InvalidOperation
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Restaurant, MenuItem, ByoComponent, RestaurantLocation


@staff_member_required
def import_menu_items(request):
    """Import menu items from CSV file."""
    restaurants = Restaurant.objects.all()

    if request.method == 'POST':
        restaurant_id = request.POST.get('restaurant')
        csv_file = request.FILES.get('csv_file')

        if not restaurant_id or not csv_file:
            messages.error(request, 'Please select a restaurant and upload a CSV file.')
            return render(request, 'admin/api/import_menu_items.html', {'restaurants': restaurants})

        restaurant = Restaurant.objects.get(pk=restaurant_id)
        imported = 0
        errors = []

        try:
            decoded = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))

            for i, row in enumerate(reader, start=2):
                try:
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
                            'saturated_fat': Decimal(row['saturated_fat']) if row.get('saturated_fat') else None,
                            'is_vegetarian': row.get('is_vegetarian', '').lower() == 'true',
                            'is_vegan': row.get('is_vegan', '').lower() == 'true',
                            'is_gluten_free': row.get('is_gluten_free', '').lower() == 'true',
                            'source_url': row.get('source_url', ''),
                            'image_url': row.get('image_url', ''),
                            'last_verified': timezone.now(),
                        }
                    )
                    imported += 1
                except (KeyError, ValueError, InvalidOperation) as e:
                    errors.append(f'Row {i}: {e}')

        except Exception as e:
            messages.error(request, f'Failed to read CSV: {e}')
            return render(request, 'admin/api/import_menu_items.html', {'restaurants': restaurants})

        restaurant.update_item_count()

        if imported:
            messages.success(request, f'Imported {imported} menu items for {restaurant.name}.')
        if errors:
            messages.warning(request, f'{len(errors)} rows had errors: {"; ".join(errors[:5])}')

        return render(request, 'admin/api/import_menu_items.html', {
            'restaurants': restaurants,
            'imported': imported,
            'errors': errors,
        })

    return render(request, 'admin/api/import_menu_items.html', {'restaurants': restaurants})


@staff_member_required
def import_locations(request):
    """Import restaurant locations from CSV file."""
    restaurants = Restaurant.objects.all()

    if request.method == 'POST':
        restaurant_id = request.POST.get('restaurant')
        csv_file = request.FILES.get('csv_file')

        if not restaurant_id or not csv_file:
            messages.error(request, 'Please select a restaurant and upload a CSV file.')
            return render(request, 'admin/api/import_locations.html', {'restaurants': restaurants})

        restaurant = Restaurant.objects.get(pk=restaurant_id)
        imported = 0
        skipped = 0
        errors = []

        try:
            decoded = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))

            for i, row in enumerate(reader, start=2):
                try:
                    osm_id = int(row['osm_id'])

                    if RestaurantLocation.objects.filter(osm_id=osm_id).exists():
                        skipped += 1
                        continue

                    latitude = Decimal(row['latitude'])
                    longitude = Decimal(row['longitude'])

                    location_name = row.get('name', restaurant.name)
                    if row.get('city'):
                        location_name = f"{restaurant.name} - {row['city']}"

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
                    )
                    imported += 1
                except (KeyError, ValueError, InvalidOperation) as e:
                    errors.append(f'Row {i}: {e}')

        except Exception as e:
            messages.error(request, f'Failed to read CSV: {e}')
            return render(request, 'admin/api/import_locations.html', {'restaurants': restaurants})

        restaurant.update_location_count()

        if imported:
            messages.success(request, f'Imported {imported} locations for {restaurant.name}.')
        if skipped:
            messages.info(request, f'Skipped {skipped} duplicate locations.')
        if errors:
            messages.warning(request, f'{len(errors)} rows had errors: {"; ".join(errors[:5])}')

        return render(request, 'admin/api/import_locations.html', {
            'restaurants': restaurants,
            'imported': imported,
            'skipped': skipped,
            'errors': errors,
        })

    return render(request, 'admin/api/import_locations.html', {'restaurants': restaurants})


@staff_member_required
def parse_nutrition_pdf(request):
    """Parse a nutrition PDF using pdfplumber + Claude API."""
    restaurants = Restaurant.objects.all()

    if request.method == 'POST':
        # Step 2: Confirm and save parsed items + BYO components
        if 'confirm' in request.POST:
            restaurant_id = request.POST.get('restaurant')
            restaurant = Restaurant.objects.get(pk=restaurant_id)
            imported_items = 0
            imported_byo = 0

            # Save menu items
            item_count = int(request.POST.get('item_count', 0))
            for i in range(item_count):
                if not request.POST.get(f'include_{i}'):
                    continue
                try:
                    MenuItem.objects.update_or_create(
                        restaurant=restaurant,
                        name=request.POST.get(f'name_{i}', ''),
                        defaults={
                            'category': request.POST.get(f'category_{i}', ''),
                            'serving_size': request.POST.get(f'serving_size_{i}', ''),
                            'calories': int(request.POST.get(f'calories_{i}', 0)),
                            'protein': Decimal(request.POST.get(f'protein_{i}', 0)),
                            'carbs': Decimal(request.POST.get(f'carbs_{i}', 0)),
                            'fat': Decimal(request.POST.get(f'fat_{i}', 0)),
                            'fiber': Decimal(request.POST.get(f'fiber_{i}')) if request.POST.get(f'fiber_{i}') else None,
                            'sodium': int(request.POST.get(f'sodium_{i}')) if request.POST.get(f'sodium_{i}') else None,
                            'sugar': Decimal(request.POST.get(f'sugar_{i}')) if request.POST.get(f'sugar_{i}') else None,
                            'saturated_fat': Decimal(request.POST.get(f'saturated_fat_{i}')) if request.POST.get(f'saturated_fat_{i}') else None,
                            'last_verified': timezone.now(),
                        }
                    )
                    imported_items += 1
                except (ValueError, InvalidOperation):
                    continue

            # Save BYO components
            byo_count = int(request.POST.get('byo_count', 0))
            for i in range(byo_count):
                if not request.POST.get(f'byo_include_{i}'):
                    continue
                try:
                    ByoComponent.objects.update_or_create(
                        restaurant=restaurant,
                        name=request.POST.get(f'byo_name_{i}', ''),
                        defaults={
                            'category': request.POST.get(f'byo_category_{i}', 'extra'),
                            'calories': int(request.POST.get(f'byo_calories_{i}', 0)),
                            'protein': Decimal(request.POST.get(f'byo_protein_{i}', 0)),
                            'carbs': Decimal(request.POST.get(f'byo_carbs_{i}', 0)),
                            'fat': Decimal(request.POST.get(f'byo_fat_{i}', 0)),
                            'fiber': Decimal(request.POST.get(f'byo_fiber_{i}')) if request.POST.get(f'byo_fiber_{i}') else None,
                            'sodium': int(request.POST.get(f'byo_sodium_{i}')) if request.POST.get(f'byo_sodium_{i}') else None,
                            'sugar': Decimal(request.POST.get(f'byo_sugar_{i}')) if request.POST.get(f'byo_sugar_{i}') else None,
                            'saturated_fat': Decimal(request.POST.get(f'byo_saturated_fat_{i}')) if request.POST.get(f'byo_saturated_fat_{i}') else None,
                        }
                    )
                    imported_byo += 1
                except (ValueError, InvalidOperation):
                    continue

            restaurant.update_item_count()
            if imported_byo:
                restaurant.has_byo = True
                restaurant.save(update_fields=['has_byo'])

            parts = []
            if imported_items:
                parts.append(f'{imported_items} menu items')
            if imported_byo:
                parts.append(f'{imported_byo} BYO components')
            messages.success(request, f'Imported {" and ".join(parts)} for {restaurant.name}.')
            return render(request, 'admin/api/parse_pdf.html', {'restaurants': restaurants})

        # Step 1: Upload and parse PDF
        restaurant_id = request.POST.get('restaurant')
        pdf_file = request.FILES.get('pdf_file')

        if not restaurant_id or not pdf_file:
            messages.error(request, 'Please select a restaurant and upload a PDF file.')
            return render(request, 'admin/api/parse_pdf.html', {'restaurants': restaurants})

        restaurant = Restaurant.objects.get(pk=restaurant_id)

        try:
            from .pdf_parser import parse_nutrition_pdf as do_parse
        except ImportError as e:
            messages.error(request, f'Missing dependency: {e}. Run: pip install pdfplumber anthropic')
            return render(request, 'admin/api/parse_pdf.html', {'restaurants': restaurants})

        try:
            from django.conf import settings

            api_key = settings.ANTHROPIC_API_KEY
            if not api_key:
                messages.error(request, 'ANTHROPIC_API_KEY not configured in settings.')
                return render(request, 'admin/api/parse_pdf.html', {'restaurants': restaurants})

            result = do_parse(pdf_file, api_key)
            menu_items = result.get('menu_items', [])
            byo_components = result.get('byo_components', [])

            return render(request, 'admin/api/parse_pdf.html', {
                'restaurants': restaurants,
                'parsed_items': menu_items,
                'parsed_byo': byo_components,
                'restaurant': restaurant,
                'item_count': len(menu_items),
                'byo_count': len(byo_components),
            })
        except Exception as e:
            messages.error(request, f'PDF parsing failed: {e}')

    return render(request, 'admin/api/parse_pdf.html', {'restaurants': restaurants})
