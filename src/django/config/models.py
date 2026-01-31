from django.db import models
from django.core.exceptions import ValidationError


class FilterConfiguration(models.Model):
    """
    Configurable filter options for the frontend.
    Supports filters like calories, protein, carbs, fat, etc.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Filter name (e.g., 'calories', 'protein')")
    label = models.CharField(max_length=100, help_text="Display label for the filter")
    unit = models.CharField(max_length=20, help_text="Unit of measurement (e.g., 'g', 'kcal')")
    options = models.JSONField(help_text="Array of filter options as JSON")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Filter Configuration"
        verbose_name_plural = "Filter Configurations"

    def __str__(self):
        return f"{self.label} ({self.name})"

    def clean(self):
        """Validate that options is a list of objects with required fields."""
        if not isinstance(self.options, list):
            raise ValidationError("Options must be a list")

        for idx, option in enumerate(self.options):
            if not isinstance(option, dict):
                raise ValidationError(f"Option {idx} must be an object")

            required_fields = ['label', 'min', 'max']
            for field in required_fields:
                if field not in option:
                    raise ValidationError(f"Option {idx} missing required field: {field}")


class QuickFilter(models.Model):
    """
    Preset filter combinations for quick access.
    Examples: High Protein, Low Carb, Balanced, etc.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Internal name/ID for the preset")
    label = models.CharField(max_length=100, help_text="Display label")
    icon = models.CharField(max_length=50, help_text="Icon name (e.g., 'Zap', 'Heart')")
    description = models.TextField(help_text="Description of what this preset does")
    filter_params = models.JSONField(help_text="Filter parameters as JSON object")
    requires_location = models.BooleanField(default=False, help_text="Whether this filter requires user location")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Quick Filter"
        verbose_name_plural = "Quick Filters"

    def __str__(self):
        return self.label

    def clean(self):
        """Validate that filter_params is a valid object."""
        if not isinstance(self.filter_params, dict):
            raise ValidationError("Filter params must be an object")


class SortOption(models.Model):
    """
    Sort options for the dish list.
    Examples: Protein (High to Low), Calories (Low to High), etc.
    """
    value = models.CharField(max_length=100, unique=True, help_text="Internal sort value (e.g., 'protein_ratio_desc')")
    label = models.CharField(max_length=100, help_text="Display label")
    requires_location = models.BooleanField(default=False, help_text="Whether this sort requires user location")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'value']
        verbose_name = "Sort Option"
        verbose_name_plural = "Sort Options"

    def __str__(self):
        return self.label


class AppConfiguration(models.Model):
    """
    Global app configuration settings (singleton pattern).
    Only one instance should exist.
    """
    default_sort = models.CharField(
        max_length=100,
        default='protein_ratio_desc',
        help_text="Default sort option"
    )
    items_per_page = models.IntegerField(
        default=20,
        help_text="Number of items per page"
    )
    radius_options = models.JSONField(
        default=list,
        help_text="Available radius options in miles (e.g., [5, 10, 25, 50])"
    )
    default_map_center = models.JSONField(
        default=list,
        help_text="Default map center [lng, lat] (e.g., [-74.0060, 40.7128])"
    )
    default_map_zoom = models.IntegerField(
        default=12,
        help_text="Default map zoom level"
    )
    version = models.IntegerField(
        default=1,
        help_text="Config version for cache invalidation"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "App Configuration"
        verbose_name_plural = "App Configuration"

    def __str__(self):
        return f"App Configuration (v{self.version})"

    def save(self, *args, **kwargs):
        """Enforce singleton pattern - only allow one instance."""
        if not self.pk and AppConfiguration.objects.exists():
            raise ValidationError("Only one AppConfiguration instance is allowed")

        # Auto-increment version on save (only if updating existing instance)
        if self.pk:
            try:
                old_instance = AppConfiguration.objects.get(pk=self.pk)
                self.version = old_instance.version + 1
            except AppConfiguration.DoesNotExist:
                # First save with pk=1, keep default version
                pass

        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance."""
        instance, created = cls.objects.get_or_create(pk=1)
        return instance
