"""Database models for Graze API."""
from decimal import Decimal
from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    website_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    logo = models.ImageField(upload_to='restaurants/logos/', blank=True, help_text='Main logo image')
    icon = models.ImageField(upload_to='restaurants/icons/', blank=True, help_text='Square icon for map markers and thumbnails')
    brand_color = models.CharField(max_length=7, blank=True, default='#3B82F6', help_text='Hex color for map markers (e.g., #FF5733)')
    nutrition_source_url = models.URLField(blank=True)
    item_count = models.PositiveIntegerField(default=0)
    location_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def update_item_count(self):
        self.item_count = self.menu_items.filter(is_available=True).count()
        self.save(update_fields=['item_count'])

    def update_location_count(self):
        self.location_count = self.locations.filter(is_active=True).count()
        self.save(update_fields=['location_count'])


class MenuItem(models.Model):
    DENSITY_THRESHOLDS = {
        'excellent': Decimal('12.0'),
        'good': Decimal('8.0'),
        'average': Decimal('5.0'),
    }

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    serving_size = models.CharField(max_length=100, blank=True)

    calories = models.PositiveIntegerField()
    protein = models.DecimalField(max_digits=5, decimal_places=1)
    carbs = models.DecimalField(max_digits=5, decimal_places=1)
    fat = models.DecimalField(max_digits=5, decimal_places=1)

    fiber = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    sodium = models.PositiveIntegerField(null=True, blank=True)
    sugar = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    saturated_fat = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)

    image_url = models.URLField(blank=True, help_text='URL to food photo thumbnail')

    is_available = models.BooleanField(default=True)
    source_url = models.URLField(blank=True)
    last_verified = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-protein']

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

    @property
    def protein_per_100cal(self):
        if self.calories == 0:
            return Decimal('0.0')
        return round(Decimal(self.protein) * 100 / self.calories, 1)

    @property
    def density_label(self):
        ratio = self.protein_per_100cal
        if ratio > self.DENSITY_THRESHOLDS['excellent']:
            return 'excellent'
        elif ratio >= self.DENSITY_THRESHOLDS['good']:
            return 'good'
        elif ratio >= self.DENSITY_THRESHOLDS['average']:
            return 'average'
        return 'low'


class DataFlag(models.Model):
    FLAG_TYPES = [
        ('incorrect', 'Incorrect Data'),
        ('outdated', 'Outdated Data'),
        ('missing', 'Missing Item'),
    ]

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='flags', null=True, blank=True)
    flag_type = models.CharField(max_length=50, choices=FLAG_TYPES)
    user_comment = models.TextField(blank=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        item = self.menu_item.name if self.menu_item else 'No item'
        return f"{self.flag_type}: {item}"


class RestaurantLocation(models.Model):
    """Physical restaurant locations with geospatial data."""

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='locations')
    osm_id = models.BigIntegerField(null=True, blank=True, db_index=True, help_text='OpenStreetMap ID')
    name = models.CharField(max_length=255, help_text='Location name (e.g., "Chipotle - Union Square")')

    # Coordinates
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    # Address
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2, default='US')

    # Contact
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)

    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_verified = models.BooleanField(default=False, help_text='Verified by admin or user')

    # Data source
    data_source = models.CharField(max_length=50, default='osm', help_text='osm, user_submission, manual')
    osm_amenity_type = models.CharField(max_length=50, blank=True, help_text='fast_food, restaurant')

    # Metadata
    last_verified = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['restaurant__name', 'city']
        indexes = [
            models.Index(fields=['restaurant']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['state']),
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.city}, {self.state}"


class LocationFlag(models.Model):
    """User-reported issues with restaurant locations."""

    FLAG_TYPES = [
        ('closed', 'Location Closed'),
        ('wrong_address', 'Wrong Address'),
        ('duplicate', 'Duplicate Entry'),
        ('missing', 'Location Missing'),
    ]

    location = models.ForeignKey(RestaurantLocation, on_delete=models.CASCADE, related_name='flags')
    flag_type = models.CharField(max_length=50, choices=FLAG_TYPES)
    user_comment = models.TextField(blank=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.flag_type}: {self.location}"
