from django.contrib import admin
from django.utils.html import mark_safe
from unfold.admin import ModelAdmin
from .models import Restaurant, MenuItem, DataFlag, RestaurantLocation, LocationFlag


@admin.register(Restaurant)
class RestaurantAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'icon_thumb', 'item_count', 'location_count', 'last_updated']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['logo_preview', 'icon_preview']
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'brand_color')}),
        ('Images', {'fields': ('logo', 'logo_preview', 'icon', 'icon_preview')}),
        ('Links', {'fields': ('website_url', 'logo_url', 'nutrition_source_url')}),
    )

    @admin.display(description='Icon')
    def icon_thumb(self, obj):
        if obj.icon:
            return mark_safe(f'<img src="{obj.icon.url}" style="width:24px;height:24px;object-fit:contain;border-radius:4px;" />')
        return '-'

    @admin.display(description='Logo Preview')
    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" style="max-width:200px;max-height:100px;" />')
        return 'No logo uploaded'

    @admin.display(description='Icon Preview')
    def icon_preview(self, obj):
        if obj.icon:
            return mark_safe(f'<img src="{obj.icon.url}" style="width:64px;height:64px;object-fit:contain;border-radius:8px;" />')
        return 'No icon uploaded'


@admin.register(MenuItem)
class MenuItemAdmin(ModelAdmin):
    list_display = ['name', 'restaurant', 'category', 'calories', 'protein', 'carbs', 'fat', 'density_label', 'is_available']
    list_filter = ['restaurant', 'category', 'is_available']
    search_fields = ['name', 'restaurant__name']


@admin.register(DataFlag)
class DataFlagAdmin(ModelAdmin):
    list_display = ['menu_item', 'flag_type', 'resolved', 'created_at']
    list_filter = ['flag_type', 'resolved']


@admin.register(RestaurantLocation)
class RestaurantLocationAdmin(ModelAdmin):
    list_display = ['restaurant', 'name', 'city', 'state', 'is_active', 'data_source']
    list_filter = ['restaurant', 'state', 'is_active', 'data_source']
    search_fields = ['name', 'city', 'address', 'restaurant__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LocationFlag)
class LocationFlagAdmin(ModelAdmin):
    list_display = ['location', 'flag_type', 'resolved', 'created_at']
    list_filter = ['flag_type', 'resolved']
    readonly_fields = ['created_at']
