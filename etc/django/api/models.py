"""
Database models for Graze API.
"""
from decimal import Decimal
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Restaurant(models.Model):
    """Restaurant chain with nutrition data."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    website_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    nutrition_source_url = models.URLField(blank=True)
    item_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def update_item_count(self):
        self.item_count = self.menu_items.filter(is_available=True).count()
        self.save(update_fields=['item_count'])


class MenuItem(models.Model):
    """Individual menu item with nutritional information."""

    DENSITY_THRESHOLDS = {
        'excellent': Decimal('12.0'),
        'good': Decimal('8.0'),
        'average': Decimal('5.0'),
    }

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='menu_items'
    )
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    serving_size = models.CharField(max_length=100, blank=True)

    # Core macros
    calories = models.PositiveIntegerField()
    protein = models.DecimalField(max_digits=5, decimal_places=1)
    carbs = models.DecimalField(max_digits=5, decimal_places=1)
    fat = models.DecimalField(max_digits=5, decimal_places=1)

    # Extended nutrition
    fiber = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    sodium = models.PositiveIntegerField(null=True, blank=True)
    sugar = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    saturated_fat = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    # Dietary flags
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    allergens = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    # Availability
    is_available = models.BooleanField(default=True)
    seasonal_note = models.CharField(max_length=255, blank=True)

    # Tracking
    popularity_score = models.PositiveIntegerField(default=0)
    source_url = models.URLField(blank=True)
    last_verified = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-protein']
        indexes = [
            models.Index(fields=['calories']),
            models.Index(fields=['protein']),
            models.Index(fields=['restaurant']),
            models.Index(fields=['category']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

    @property
    def protein_per_100cal(self) -> Decimal:
        """Calculate grams of protein per 100 calories."""
        if self.calories == 0:
            return Decimal('0.0')
        return round(Decimal(self.protein) * 100 / self.calories, 1)

    @property
    def density_label(self) -> str:
        """Return protein density category label."""
        ratio = self.protein_per_100cal
        if ratio > self.DENSITY_THRESHOLDS['excellent']:
            return 'excellent'
        elif ratio >= self.DENSITY_THRESHOLDS['good']:
            return 'good'
        elif ratio >= self.DENSITY_THRESHOLDS['average']:
            return 'average'
        return 'low'


class DataFlag(models.Model):
    """User-reported data issues."""
    FLAG_TYPES = [
        ('incorrect', 'Incorrect Data'),
        ('outdated', 'Outdated Data'),
        ('missing', 'Missing Item'),
    ]

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='flags',
        null=True,
        blank=True
    )
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


class WaitlistEntry(models.Model):
    """Email waitlist signup."""
    email = models.EmailField(unique=True)
    source = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Waitlist entries'
        ordering = ['-created_at']

    def __str__(self):
        return self.email
