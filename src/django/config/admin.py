from django.contrib import admin
from .models import FilterConfiguration, QuickFilter, SortOption, AppConfiguration


@admin.register(FilterConfiguration)
class FilterConfigurationAdmin(admin.ModelAdmin):
    """
    Admin interface for filter configurations.
    """
    list_display = ('name', 'label', 'unit', 'is_active', 'order', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'label')
    ordering = ('order', 'name')
    list_editable = ('is_active', 'order')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'label', 'unit', 'is_active', 'order')
        }),
        ('Filter Options', {
            'fields': ('options',),
            'description': 'Enter filter options as JSON array. Example: [{"label": "Low (0-300)", "min": 0, "max": 300}, {"label": "Medium (300-600)", "min": 300, "max": 600}]'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        """Make name readonly after creation to prevent breaking frontend references."""
        if obj:  # Editing existing object
            return self.readonly_fields + ('name',)
        return self.readonly_fields


@admin.register(QuickFilter)
class QuickFilterAdmin(admin.ModelAdmin):
    """
    Admin interface for quick filter presets.
    """
    list_display = ('name', 'label', 'icon', 'requires_location', 'is_active', 'order', 'updated_at')
    list_filter = ('is_active', 'requires_location')
    search_fields = ('name', 'label', 'description')
    ordering = ('order', 'name')
    list_editable = ('is_active', 'order')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'label', 'icon', 'description', 'is_active', 'order')
        }),
        ('Configuration', {
            'fields': ('requires_location', 'filter_params'),
            'description': 'Filter params example: {"calories": {"min": 0, "max": 500}, "protein": {"min": 30, "max": null}, "sort": "protein_ratio_desc"}'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        """Make name readonly after creation to prevent breaking frontend references."""
        if obj:  # Editing existing object
            return self.readonly_fields + ('name',)
        return self.readonly_fields


@admin.register(SortOption)
class SortOptionAdmin(admin.ModelAdmin):
    """
    Admin interface for sort options.
    """
    list_display = ('value', 'label', 'requires_location', 'is_active', 'order', 'updated_at')
    list_filter = ('is_active', 'requires_location')
    search_fields = ('value', 'label')
    ordering = ('order', 'value')
    list_editable = ('is_active', 'order')

    fieldsets = (
        ('Basic Information', {
            'fields': ('value', 'label', 'is_active', 'order')
        }),
        ('Requirements', {
            'fields': ('requires_location',),
            'description': 'Check if this sort option requires user location (e.g., "Distance" sort)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def get_readonly_fields(self, request, obj=None):
        """Make value readonly after creation to prevent breaking frontend references."""
        if obj:  # Editing existing object
            return self.readonly_fields + ('value',)
        return self.readonly_fields


@admin.register(AppConfiguration)
class AppConfigurationAdmin(admin.ModelAdmin):
    """
    Admin interface for app configuration (singleton).
    """
    fieldsets = (
        ('Pagination & Defaults', {
            'fields': ('default_sort', 'items_per_page')
        }),
        ('Location Settings', {
            'fields': ('radius_options',),
            'description': 'Available radius options in miles. Example: [5, 10, 25, 50]'
        }),
        ('Map Defaults', {
            'fields': ('default_map_center', 'default_map_zoom'),
            'description': 'Map center format: [longitude, latitude]. Example: [-74.0060, 40.7128] for NYC'
        }),
        ('Version Control', {
            'fields': ('version', 'updated_at'),
            'description': 'Version auto-increments on save for cache invalidation'
        }),
    )

    readonly_fields = ('version', 'updated_at')

    def has_add_permission(self, request):
        """Prevent adding more than one instance (singleton)."""
        return not AppConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting the singleton instance."""
        return False
