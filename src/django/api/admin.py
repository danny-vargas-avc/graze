from django.contrib import admin
from .models import Restaurant, MenuItem, DataFlag, RestaurantLocation, LocationFlag


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'item_count', 'location_count', 'last_updated']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'category', 'calories', 'protein', 'carbs', 'fat', 'density_label', 'is_available']
    list_filter = ['restaurant', 'category', 'is_available']
    search_fields = ['name', 'restaurant__name']


@admin.register(DataFlag)
class DataFlagAdmin(admin.ModelAdmin):
    list_display = ['menu_item', 'flag_type', 'resolved', 'created_at']
    list_filter = ['flag_type', 'resolved']


@admin.register(RestaurantLocation)
class RestaurantLocationAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'name', 'city', 'state', 'is_active', 'data_source']
    list_filter = ['restaurant', 'state', 'is_active', 'data_source']
    search_fields = ['name', 'city', 'address', 'restaurant__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LocationFlag)
class LocationFlagAdmin(admin.ModelAdmin):
    list_display = ['location', 'flag_type', 'resolved', 'created_at']
    list_filter = ['flag_type', 'resolved']
    readonly_fields = ['created_at']
